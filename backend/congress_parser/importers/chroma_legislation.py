"""
ChromaDB importer for bill text (every legislation version).

Embeds section-level slices of each parsed ``legislation_version`` into the
ChromaDB "legislation" collection using OpenAI text-embedding-3-small, so that
``congress_fastapi.handlers.legislation.text_search`` can answer conceptual
queries and map hits back to ``legislation_content`` rows.

Usage
-----
# Embed every completed version that is missing or stale (backfill + incremental):
    python3 -m congress_parser.importers.chroma_legislation

# Only specific versions / a whole bill:
    python3 -m congress_parser.importers.chroma_legislation --version-id 123 --version-id 124
    python3 -m congress_parser.importers.chroma_legislation --legislation-id 456

# Wipe the collection and rebuild:
    python3 -m congress_parser.importers.chroma_legislation --reset

# Count what would be embedded (and a rough token estimate) without calling OpenAI:
    python3 -m congress_parser.importers.chroma_legislation --dry-run

Incremental sync
----------------
No Postgres tracking column is used. Chunk 0 of every embedded version carries
the version's ``completed_at`` timestamp in its Chroma metadata. A version is
(re)embedded when it has no chunk 0, or when the stored timestamp differs from
``legislation_version.completed_at`` (i.e. the version was re-parsed). Re-embedding
first deletes the version's old chunks, since content row ids change on re-parse.
Run this after the bill parse job; it is safe to run repeatedly.

Prerequisites
-------------
- Bills parsed into PostgreSQL (congress_parser.importers.bills)
- ChromaDB reachable (CHROMA_HOST / CHROMA_PORT)
- OPENAI_API_KEY set
"""

import argparse
import asyncio
import sys
from typing import List, Optional
from urllib.error import URLError

import chromadb
from chromadb.config import Settings

from congress_fastapi.db.postgres import get_database
from congress_parser.bill_documents import (
    bill_label,
    bill_type_code,
    build_document,
    build_section_chunks,
)
from congress_parser.embeddings import EMBEDDING_MODEL, embed_texts
from congress_parser.importers.chroma_uscode import (
    CHROMA_DATABASE,
    CHROMA_HOST,
    CHROMA_PORT,
    CHROMA_TENANT,
    ensure_chroma_tenant_and_db,
)

COLLECTION_NAME = "legislation"
DEFAULT_VERSION_BATCH = 50
UPSERT_BATCH = 500


async def open_collection(reset: bool):
    client = await chromadb.AsyncHttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT,
        ssl=False,
        headers=None,
        settings=Settings(),
        tenant=CHROMA_TENANT,
        database=CHROMA_DATABASE,
    )
    if reset:
        try:
            await client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'.")
        except Exception:
            pass
    # embedding_function=None: vectors are always supplied explicitly.
    return await client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", "embedding_model": EMBEDDING_MODEL},
        embedding_function=None,
    )


CANDIDATE_SQL = """
    SELECT lv.legislation_version_id, lv.legislation_version, lv.legislation_id,
           lv.completed_at, lv.effective_date,
           l.chamber, l.legislation_type, l.number, l.title, l.congress_id
    FROM legislation_version lv
    JOIN legislation l ON l.legislation_id = lv.legislation_id
    WHERE lv.completed_at IS NOT NULL
      {filters}
    ORDER BY lv.legislation_version_id
"""


async def fetch_candidates(
    database, version_ids: Optional[List[int]], legislation_id: Optional[int]
):
    filters, values = [], {}
    if version_ids:
        filters.append("AND lv.legislation_version_id = ANY(:vids)")
        values["vids"] = version_ids
    if legislation_id is not None:
        filters.append("AND lv.legislation_id = :lid")
        values["lid"] = legislation_id
    return await database.fetch_all(
        CANDIDATE_SQL.format(filters=" ".join(filters)), values=values
    )


async def stale_versions(collection, candidates) -> list:
    """Return candidates whose chunk 0 is missing or was embedded from an older parse."""
    ids = [c["legislation_version_id"] for c in candidates]
    found = await collection.get(
        where={
            "$and": [
                {"legislation_version_id": {"$in": ids}},
                {"chunk_index": 0},
            ]
        },
        include=["metadatas"],
    )
    embedded = {}
    for meta in found["metadatas"]:
        embedded.setdefault(meta["legislation_version_id"], set()).add(
            meta["completed_at"]
        )
    return [
        c
        for c in candidates
        # a version can have several chunk-0s (one per section); any stale one
        # means the version must be rebuilt
        if embedded.get(c["legislation_version_id"]) != {c["completed_at"].isoformat()}
    ]


async def embed_version(database, collection, version, dry_run: bool) -> tuple:
    """Returns (chunks, approx_tokens) for the version."""
    rows = await database.fetch_all(
        """
        SELECT legislation_content_id, parent_id, order_number, lc_ident,
               section_display, heading, content_str, content_type
        FROM legislation_content
        WHERE legislation_version_id = :vid
        """,
        values={"vid": version["legislation_version_id"]},
    )
    chunks = build_section_chunks([dict(r) for r in rows])

    chamber = str(version["chamber"]).split(".")[-1]
    leg_type = str(version["legislation_type"]).split(".")[-1]
    ver = str(version["legislation_version"]).split(".")[-1]
    label = bill_label(chamber, leg_type, version["number"], version["congress_id"])
    documents = [build_document(f"{label} {ver}", version["title"], c) for c in chunks]
    approx_tokens = sum(len(d) for d in documents) // 4
    if dry_run or not chunks:
        if not dry_run:
            await collection.delete(
                where={"legislation_version_id": version["legislation_version_id"]}
            )
        return len(chunks), approx_tokens

    completed_at = version["completed_at"].isoformat()
    effective = version["effective_date"]
    base_meta = {
        "legislation_id": version["legislation_id"],
        "legislation_version_id": version["legislation_version_id"],
        "version": ver,
        "congress": version["congress_id"],
        "chamber": chamber,
        "bill_type": bill_type_code(chamber, leg_type),
        "number": version["number"],
        "bill_title": (version["title"] or "")[:300],
        "completed_at": completed_at,
    }
    if effective:
        base_meta["effective_date"] = effective.isoformat()

    # Old chunk ids are keyed on content ids, which change on re-parse.
    await collection.delete(
        where={"legislation_version_id": version["legislation_version_id"]}
    )
    for start in range(0, len(chunks), UPSERT_BATCH):
        part = slice(start, start + UPSERT_BATCH)
        vectors = await asyncio.to_thread(embed_texts, documents[part])
        await collection.upsert(
            ids=[
                f"{version['legislation_version_id']}:{c.legislation_content_id}:{c.chunk_index}"
                for c in chunks[part]
            ],
            embeddings=vectors,
            documents=documents[part],
            metadatas=[
                {
                    **base_meta,
                    "legislation_content_id": c.legislation_content_id,
                    "lc_ident": c.lc_ident or "",
                    "section_display": c.section_display[:100],
                    "heading": c.heading[:200],
                    "chunk_index": c.chunk_index,
                    "chunk_count": c.chunk_count,
                    "char_count": len(d),
                }
                for c, d in zip(chunks[part], documents[part])
            ],
        )
    return len(chunks), approx_tokens


async def run_import(
    version_ids: Optional[List[int]],
    legislation_id: Optional[int],
    batch_size: int,
    reset: bool,
    dry_run: bool,
):
    database = await get_database()
    candidates = await fetch_candidates(database, version_ids, legislation_id)
    print(f"Completed versions in scope: {len(candidates):,}")

    try:
        ensure_chroma_tenant_and_db()
    except URLError as exc:
        print(f"Could not reach ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}: {exc}", file=sys.stderr)
        sys.exit(1)
    collection = await open_collection(reset=reset)

    total_chunks = total_tokens = versions_done = 0
    for start in range(0, len(candidates), batch_size):
        batch = candidates[start : start + batch_size]
        todo = await stale_versions(collection, batch)
        for version in todo:
            chunks, tokens = await embed_version(database, collection, version, dry_run)
            total_chunks += chunks
            total_tokens += tokens
            versions_done += 1
        print(
            f"  scanned {min(start + batch_size, len(candidates)):,}/{len(candidates):,}  "
            f"{'would embed' if dry_run else 'embedded'} {versions_done:,} versions, "
            f"{total_chunks:,} chunks, ~{total_tokens:,} tokens",
            end="\r",
            flush=True,
        )
    print(
        f"\nDone. {versions_done:,} versions, {total_chunks:,} chunks, "
        f"~{total_tokens:,} tokens (~${total_tokens / 1e6 * 0.02:.2f} at $0.02/1M)."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Embed bill text sections into ChromaDB for semantic search.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--reset", action="store_true", help="Delete the collection first.")
    parser.add_argument("--dry-run", action="store_true", help="Count only; no OpenAI calls or writes.")
    parser.add_argument("--version-id", type=int, action="append", help="legislation_version_id (repeatable).")
    parser.add_argument("--legislation-id", type=int, help="Embed all versions of one bill.")
    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_VERSION_BATCH,
        help=f"Versions checked/processed per round (default {DEFAULT_VERSION_BATCH}).",
    )
    args = parser.parse_args()
    asyncio.run(
        run_import(
            args.version_id, args.legislation_id, args.batch_size, args.reset, args.dry_run
        )
    )


if __name__ == "__main__":
    main()
