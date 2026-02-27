"""
ChromaDB importer for US Code sections.

Reads top-level USC sections from PostgreSQL and indexes them into the ChromaDB
"uscode" collection so that the interest-based code linking feature can perform
semantic search against them.

Usage
-----
# Index the latest USC release (auto-detected):
    python3 -m congress_parser.importers.chroma_uscode

# Wipe the collection and re-index from scratch:
    python3 -m congress_parser.importers.chroma_uscode --reset

# Specify an explicit version_id (matches the hardcoded value in uscode.py):
    python3 -m congress_parser.importers.chroma_uscode --version-id 74573

# Check what would be indexed without writing anything:
    python3 -m congress_parser.importers.chroma_uscode --dry-run

# Tune throughput (default batch size is 200):
    python3 -m congress_parser.importers.chroma_uscode --batch-size 500

Prerequisites
-------------
- US Code data must already be in PostgreSQL (run congress_parser.importers.releases first)
- ChromaDB service must be running (docker-compose up congress_chromadb)
- CHROMA_HOST env var must point to the ChromaDB host (default: congress_chromadb)
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Optional
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

import chromadb
from chromadb.config import Settings

from congress_fastapi.db.postgres import get_database

# ── Configuration ────────────────────────────────────────────────────────────

CHROMA_HOST = (
    os.environ.get(
        "CHROMA_HOST",
        os.environ.get("LLM_HOST", "localhost"),
    )
    .split("http://")[-1]
    .split(":")[0]
)
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
CHROMA_TENANT = "congress-dev"
CHROMA_DATABASE = "usc-chat"
COLLECTION_NAME = "uscode"
DEFAULT_BATCH_SIZE = 200


# ── Database helpers ──────────────────────────────────────────────────────────


async def get_latest_version_id(database) -> int:
    """Return the version_id associated with the most recent USC release point."""
    row = await database.fetch_one(
        """
        SELECT v.version_id
        FROM version v
        JOIN usc_release ur ON ur.version_id = v.version_id
        WHERE ur.effective_date IS NOT NULL
        ORDER BY ur.effective_date DESC
        LIMIT 1
        """
    )
    if row is None:
        raise RuntimeError(
            "No USC release points found in the database.\n"
            "Run 'python3 -m congress_parser.importers.releases' first."
        )
    return row[0]


async def count_sections(database, version_id: int) -> int:
    """Count indexable top-level USC sections for this version."""
    row = await database.fetch_one(
        """
        SELECT COUNT(*)
        FROM usc_content
        WHERE version_id = :vid
          AND usc_ident ~ '^/us/usc/t[0-9]+/s[^/]+$'
          AND heading IS NOT NULL
          AND heading != ''
        """,
        values={"vid": version_id},
    )
    return row[0]


async def fetch_sections_batch(
    database, version_id: int, offset: int, batch_size: int
) -> list:
    """
    Fetch one page of top-level USC sections, joined to their title name.

    Filters to identifiers of the form /us/usc/t{n}/s{identifier} — these are
    the IDs stored in ChromaDB and resolved back to Postgres in search_chroma().
    """
    return await database.fetch_all(
        """
        SELECT
            uc.usc_ident,
            uc.heading,
            uc.content_str,
            uc.number,
            uc.section_display,
            ch.long_title  AS chapter_title,
            ch.short_title AS chapter_short_title
        FROM usc_content uc
        JOIN usc_section  us_sec ON us_sec.usc_section_id  = uc.usc_section_id
        JOIN usc_chapter  ch     ON ch.usc_chapter_id      = us_sec.usc_chapter_id
        WHERE uc.version_id = :vid
          AND uc.usc_ident ~ '^/us/usc/t[0-9]+/s[^/]+$'
          AND uc.heading IS NOT NULL
          AND uc.heading != ''
        ORDER BY uc.usc_ident
        LIMIT  :lim
        OFFSET :off
        """,
        values={"vid": version_id, "lim": batch_size, "off": offset},
    )


def build_document(row) -> str:
    """
    Build the text that ChromaDB will embed for a USC section.

    Format: "<Title long name> — §<number>. <heading>\\n<content>"
    The title name helps the embedding model place sections in context.
    """
    parts = []
    chapter_title = (row["chapter_title"] or "").strip().capitalize()
    if chapter_title:
        parts.append(chapter_title)
    if row["section_display"]:
        section_label = row["section_display"].strip()
        heading = (row["heading"] or "").strip()
        if heading:
            parts.append(f"{section_label}. {heading}")
        else:
            parts.append(section_label)
    elif row["heading"]:
        parts.append(row["heading"].strip())
    header = " — ".join(parts)

    content = (row["content_str"] or "").strip()
    if content:
        # Truncate very long sections to stay within typical embedding limits
        content = content[:8000]
        return f"{header}\n{content}" if header else content
    return header


# ── ChromaDB setup ─────────────────────────────────────────────────────────────


def _chroma_rest(method: str, path: str, body: Optional[dict] = None):
    """Make a raw HTTP call to the ChromaDB admin REST API."""
    url = f"http://{CHROMA_HOST}:{CHROMA_PORT}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib_request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    try:
        with urllib_request.urlopen(req, timeout=10) as resp:
            return resp.status
    except HTTPError as exc:
        return exc.code  # Return status code; callers decide what's acceptable


def ensure_chroma_tenant_and_db():
    """
    Create the ChromaDB tenant and database if they do not already exist.

    HTTP 422 means the resource already exists (ChromaDB's behaviour); we
    treat that the same as HTTP 200.
    """
    # Tenant
    status = _chroma_rest("POST", "/api/v1/tenants", {"name": CHROMA_TENANT})
    if status not in (200, 201, 422, 409):
        print(
            f"Warning: unexpected HTTP {status} when creating tenant '{CHROMA_TENANT}'. "
            "Proceeding anyway.",
            file=sys.stderr,
        )

    # Database (scoped to tenant via query param)
    status = _chroma_rest(
        "POST",
        f"/api/v1/databases?tenant={CHROMA_TENANT}",
        {"name": CHROMA_DATABASE},
    )
    if status not in (200, 201, 422, 409):
        print(
            f"Warning: unexpected HTTP {status} when creating database '{CHROMA_DATABASE}'. "
            "Proceeding anyway.",
            file=sys.stderr,
        )


async def open_chroma_collection(reset: bool):
    """Connect to ChromaDB and return the 'uscode' collection."""
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
            pass  # Didn't exist yet

    collection = await client.get_or_create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    count = await collection.count()
    if count > 0 and not reset:
        print(
            f"Collection '{COLLECTION_NAME}' already contains {count:,} documents. "
            "Upserting will add new and update changed sections.\n"
            "Use --reset to wipe and rebuild from scratch."
        )
    return collection


# ── Main import logic ──────────────────────────────────────────────────────────


async def run_import(
    version_id: Optional[int],
    batch_size: int,
    reset: bool,
    dry_run: bool,
):
    database = await get_database()

    # Determine version
    if version_id is None:
        version_id = await get_latest_version_id(database)
        print(f"Auto-detected latest USC version_id: {version_id}")
    else:
        print(f"Using specified version_id: {version_id}")

    total = await count_sections(database, version_id)
    print(f"Sections eligible for indexing: {total:,}")

    if total == 0:
        print(
            "\nNo sections found. Make sure the USC data has been loaded:\n"
            "  python3 -m congress_parser.importers.releases",
            file=sys.stderr,
        )
        sys.exit(1)

    if dry_run:
        print("Dry-run mode — exiting without writing to ChromaDB.")
        return

    # ── ChromaDB setup ──────────────────────────────────────────
    print(f"\nConnecting to ChromaDB at {CHROMA_HOST}:{CHROMA_PORT} …")
    try:
        ensure_chroma_tenant_and_db()
    except URLError as exc:
        print(
            f"Could not reach ChromaDB at {CHROMA_HOST}:{CHROMA_PORT}: {exc}\n"
            "Is the container running?  docker-compose up congress_chromadb",
            file=sys.stderr,
        )
        sys.exit(1)

    collection = await open_chroma_collection(reset=reset)
    print(f"Opened collection '{COLLECTION_NAME}'. Starting import…\n")

    # ── Batch loop ──────────────────────────────────────────────
    offset = 0
    indexed = 0
    skipped = 0

    while offset < total:
        rows = await fetch_sections_batch(database, version_id, offset, batch_size)
        if not rows:
            break

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for row in rows:
            usc_ident: str = row["usc_ident"]
            doc_text = build_document(row)
            if not doc_text.strip():
                skipped += 1
                continue

            # Extract title number from ident: /us/usc/t42/s1395 → "42"
            parts = usc_ident.split("/")
            title_num = parts[3].lstrip("t") if len(parts) > 3 else ""

            ids.append(usc_ident)
            documents.append(doc_text)
            metadatas.append(
                {
                    "title": title_num,
                    "number": row["number"] or "",
                    "section_display": row["section_display"] or "",
                    "heading": (row["heading"] or "")[:200],
                }
            )

        if ids:
            await collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            indexed += len(ids)

        offset += batch_size
        done = min(offset, total)
        pct = done / total * 100
        print(
            f"  {done:>{len(str(total))}}/{total} ({pct:5.1f}%)  "
            f"indexed: {indexed:,}",
            end="\r",
            flush=True,
        )

    print(f"\n\nDone.  Indexed {indexed:,} sections, skipped {skipped:,} empty.")
    final_count = await collection.count()
    print(f"Collection '{COLLECTION_NAME}' now contains {final_count:,} documents.")


# ── CLI entry point ────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Index US Code sections into ChromaDB for semantic interest-based search."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the ChromaDB collection before indexing.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        metavar="N",
        help=f"Documents per upsert batch (default: {DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--version-id",
        type=int,
        default=None,
        metavar="ID",
        help=(
            "Specific usc_content.version_id to index "
            "(default: latest usc_release)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count eligible sections and exit without writing to ChromaDB.",
    )
    args = parser.parse_args()

    asyncio.run(
        run_import(
            version_id=args.version_id,
            batch_size=args.batch_size,
            reset=args.reset,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
