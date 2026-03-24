"""
Congressional Record debate summarizer.

Generates LLM summaries at two levels:
    1. Granule-level: Summarizes each debate/segment individually
    2. Daily-level: Aggregates granule summaries into per-chamber daily overviews

Follows the section_summarizer.py pattern with PromptBatch tracking.
"""

import json
import logging
from datetime import datetime
from typing import List

from congress_db.models import (
    CRECGranule,
    CRECIssue,
    CRECSpeech,
    CRECSummary,
    PromptBatch,
)
from congress_db.session import Session
from congress_parser.prompt_runners.utils import run_query

logger = logging.getLogger(__name__)

GRANULE_SUMMARY_PROMPT = """Summarize the following Congressional debate transcript.
Identify:
- The key topics discussed
- Which legislators spoke and their positions
- Any bills or legislation referenced
- Key arguments made for and against

Keep the summary to 2-3 concise paragraphs. Output JSON with a "summary" key.

TRANSCRIPT:
{transcript}"""

DAILY_SUMMARY_PROMPT = """Summarize the following Congressional Record summaries for a single day.
These are summaries of individual debates and proceedings from the {chamber}.

Provide a cohesive overview of the day's activities in 2-3 paragraphs. Output JSON with a "summary" key.

SUMMARIES:
{summaries}"""


def build_transcript(speeches: List[CRECSpeech]) -> str:
    """Build a formatted transcript from speech segments."""
    lines = []
    for speech in speeches:
        speaker = speech.speaker_raw or "UNKNOWN"
        lines.append(f"{speaker}: {speech.content_text}")
    return "\n\n".join(lines)


def summarize_granule(granule_id: int, model: str = "ollama/gemma2:27b") -> str:
    """Generate a summary for a single granule (debate segment)."""
    with Session() as session:
        speeches = (
            session.query(CRECSpeech)
            .filter(CRECSpeech.crec_granule_id == granule_id)
            .order_by(CRECSpeech.order_number)
            .all()
        )

        if not speeches:
            return None

        transcript = build_transcript(speeches)

        if len(transcript) < 100:
            return None

        # Truncate very long transcripts to fit context
        if len(transcript) > 50000:
            transcript = transcript[:50000] + "\n\n[TRUNCATED]"

        prompt = GRANULE_SUMMARY_PROMPT.format(transcript=transcript)

        try:
            response = run_query(
                prompt,
                model=model,
                num_ctx=32768,
                json=True,
                max_tokens=2000,
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return parsed.get("summary", content)
        except Exception as e:
            logger.error(f"Failed to summarize granule {granule_id}: {e}")
            return None


def summarize_daily_chamber(
    issue_id: int, chamber: str, granule_summaries: List[str],
    model: str = "ollama/gemma2:27b",
) -> str:
    """Generate a daily chamber-level summary from granule summaries."""
    if not granule_summaries:
        return None

    combined = "\n\n---\n\n".join(granule_summaries)

    if len(combined) > 30000:
        combined = combined[:30000] + "\n\n[TRUNCATED]"

    prompt = DAILY_SUMMARY_PROMPT.format(
        chamber=chamber,
        summaries=combined,
    )

    try:
        response = run_query(
            prompt,
            model=model,
            num_ctx=32768,
            json=True,
            max_tokens=2000,
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed.get("summary", content)
    except Exception as e:
        logger.error(f"Failed to summarize daily {chamber} for issue {issue_id}: {e}")
        return None


def run_crec_summarizer(prompt_id: int = None, model: str = "ollama/gemma2:27b"):
    """
    Summarize all unsummarized Congressional Record granules and daily issues.
    """
    with Session() as session:
        # Find granules without summaries
        summarized_granule_ids = (
            session.query(CRECSummary.crec_granule_id)
            .filter(
                CRECSummary.crec_granule_id.isnot(None),
                CRECSummary.summary_type == "granule",
            )
            .subquery()
        )

        unsummarized_granules = (
            session.query(CRECGranule)
            .filter(CRECGranule.crec_granule_id.notin_(
                session.query(summarized_granule_ids)
            ))
            .order_by(CRECGranule.crec_granule_id.desc())
            .all()
        )

        logger.info(f"Found {len(unsummarized_granules)} unsummarized granules")

        prompt_batch = PromptBatch(
            prompt_id=prompt_id,
            legislation_version_id=None,
            attempted=0,
            successful=0,
            failed=0,
            skipped=0,
            created_at=datetime.now(),
        )
        session.add(prompt_batch)
        session.commit()

        for granule in unsummarized_granules:
            prompt_batch.attempted += 1

            summary_text = summarize_granule(granule.crec_granule_id, model=model)
            if summary_text:
                summary = CRECSummary(
                    crec_granule_id=granule.crec_granule_id,
                    crec_issue_id=granule.crec_issue_id,
                    summary=summary_text,
                    summary_type="granule",
                    prompt_batch_id=prompt_batch.prompt_batch_id,
                )
                session.add(summary)
                prompt_batch.successful += 1
            else:
                prompt_batch.skipped += 1

            session.commit()

        # Now generate daily summaries for issues with granule summaries but no daily summary
        summarized_issue_ids = (
            session.query(CRECSummary.crec_issue_id)
            .filter(
                CRECSummary.crec_issue_id.isnot(None),
                CRECSummary.summary_type == "daily",
            )
            .subquery()
        )

        issues_needing_daily = (
            session.query(CRECIssue)
            .filter(CRECIssue.crec_issue_id.notin_(
                session.query(summarized_issue_ids)
            ))
            .order_by(CRECIssue.issue_date.desc())
            .all()
        )

        for issue in issues_needing_daily:
            granule_summaries_by_chamber = {}
            granule_summaries = (
                session.query(CRECSummary)
                .join(CRECGranule, CRECSummary.crec_granule_id == CRECGranule.crec_granule_id)
                .filter(
                    CRECSummary.crec_issue_id == issue.crec_issue_id,
                    CRECSummary.summary_type == "granule",
                )
                .all()
            )

            for gs in granule_summaries:
                granule = session.query(CRECGranule).get(gs.crec_granule_id)
                if granule:
                    chamber = granule.section.value if granule.section else "Unknown"
                    if chamber not in granule_summaries_by_chamber:
                        granule_summaries_by_chamber[chamber] = []
                    granule_summaries_by_chamber[chamber].append(gs.summary)

            for chamber, summaries in granule_summaries_by_chamber.items():
                prompt_batch.attempted += 1
                daily_text = summarize_daily_chamber(
                    issue.crec_issue_id, chamber, summaries, model=model,
                )
                if daily_text:
                    daily_summary = CRECSummary(
                        crec_issue_id=issue.crec_issue_id,
                        summary=daily_text,
                        summary_type="daily",
                        prompt_batch_id=prompt_batch.prompt_batch_id,
                    )
                    session.add(daily_summary)
                    prompt_batch.successful += 1
                else:
                    prompt_batch.skipped += 1

                session.commit()

        prompt_batch.completed_at = datetime.now()
        session.commit()
        logger.info(
            f"Summarization complete: {prompt_batch.successful} successful, "
            f"{prompt_batch.failed} failed, {prompt_batch.skipped} skipped"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_crec_summarizer()
