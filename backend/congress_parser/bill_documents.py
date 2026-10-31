"""
Turns the ``legislation_content`` tree of one bill version into embeddable
section-level documents.

Pure functions only (no DB / Chroma / network) so they are unit-testable.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

# Max characters of body text per chunk (~1,000 tokens). Sections longer than
# this are split on node boundaries; a single oversized node is split on
# whitespace.
MAX_CHUNK_CHARS = 4000


@dataclass
class SectionChunk:
    legislation_content_id: int
    lc_ident: Optional[str]
    section_display: str
    heading: str
    chunk_index: int
    chunk_count: int
    text: str  # body text, without the context header


def _label(row) -> str:
    return " ".join(
        part.strip() for part in (row["section_display"], row["heading"]) if part
    )


def _node_lines(row) -> List[str]:
    lines = []
    label = _label(row)
    body = (row["content_str"] or "").strip()
    if label and body:
        lines.append(f"{label} {body}")
    elif label or body:
        lines.append(label or body)
    return lines


def _split_long(line: str, limit: int) -> List[str]:
    pieces, current = [], ""
    for word in line.split():
        if current and len(current) + 1 + len(word) > limit:
            pieces.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        pieces.append(current)
    return pieces


def _chunk_lines(lines: List[str], limit: int) -> List[str]:
    chunks, current, size = [], [], 0
    for line in lines:
        for piece in _split_long(line, limit) if len(line) > limit else [line]:
            if current and size + len(piece) + 1 > limit:
                chunks.append("\n".join(current))
                current, size = [], 0
            current.append(piece)
            size += len(piece) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks


def build_section_chunks(
    rows: List[dict], max_chunk_chars: int = MAX_CHUNK_CHARS
) -> List[SectionChunk]:
    """
    ``rows`` are the ``legislation_content`` rows of a single version.

    Units are the outermost ``section`` nodes (quoted sections nested inside
    another section stay part of their parent). If a version has no section
    nodes (e.g. a simple resolution) the children of the root ``legis-body``
    node are used instead.
    """
    by_id: Dict[int, dict] = {r["legislation_content_id"]: r for r in rows}
    children = defaultdict(list)
    for r in rows:
        children[r["parent_id"]].append(r)
    for kids in children.values():
        kids.sort(key=lambda r: (r["order_number"] or 0, r["legislation_content_id"]))

    def has_section_ancestor(row) -> bool:
        parent = by_id.get(row["parent_id"])
        while parent is not None:
            if parent["content_type"] == "section":
                return True
            parent = by_id.get(parent["parent_id"])
        return False

    units = [
        r for r in rows if r["content_type"] == "section" and not has_section_ancestor(r)
    ]
    if not units:
        roots = [r for r in rows if r["parent_id"] not in by_id]
        units = [kid for root in roots for kid in children[root["legislation_content_id"]]]
    units.sort(key=lambda r: (r["order_number"] or 0, r["legislation_content_id"]))

    def walk(row) -> List[str]:
        lines = _node_lines(row)
        for kid in children[row["legislation_content_id"]]:
            lines.extend(walk(kid))
        return lines

    result: List[SectionChunk] = []
    for unit in units:
        lines = walk(unit)
        if not lines:
            continue
        texts = _chunk_lines(lines, max_chunk_chars)
        for i, text in enumerate(texts):
            result.append(
                SectionChunk(
                    legislation_content_id=unit["legislation_content_id"],
                    lc_ident=unit["lc_ident"],
                    section_display=(unit["section_display"] or "").strip(),
                    heading=(unit["heading"] or "").strip(),
                    chunk_index=i,
                    chunk_count=len(texts),
                    text=text,
                )
            )
    return result


def build_document(
    bill_label: str, bill_title: Optional[str], chunk: SectionChunk
) -> str:
    """Context header + body: this is the text that gets embedded and stored."""
    header_parts = [bill_label]
    if bill_title:
        header_parts.append(bill_title.strip())
    section = " ".join(p for p in (chunk.section_display, chunk.heading) if p)
    if section:
        header_parts.append(section)
    return f"{' — '.join(header_parts)}\n{chunk.text}"


_BILL_TYPE_CODES = {
    ("House", "Bill"): ("hr", "H.R."),
    ("Senate", "Bill"): ("s", "S."),
    ("House", "JRes"): ("hjres", "H.J.Res."),
    ("Senate", "JRes"): ("sjres", "S.J.Res."),
    ("House", "CRes"): ("hconres", "H.Con.Res."),
    ("Senate", "CRes"): ("sconres", "S.Con.Res."),
    ("House", "Res"): ("hres", "H.Res."),
    ("Senate", "Res"): ("sres", "S.Res."),
}


def bill_type_code(chamber: str, legislation_type: str) -> str:
    """e.g. ("House", "Bill") -> "hr". Arguments are the enum names stored in Postgres."""
    return _BILL_TYPE_CODES.get((chamber, legislation_type), ("", ""))[0]


def bill_label(chamber: str, legislation_type: str, number: int, congress: int) -> str:
    """e.g. "H.R. 1234 (118th Congress)"."""
    prefix = _BILL_TYPE_CODES.get((chamber, legislation_type), ("", ""))[1]
    suffix = "th"
    if congress % 100 not in (11, 12, 13):
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(congress % 10, "th")
    return f"{prefix} {number} ({congress}{suffix} Congress)".strip()
