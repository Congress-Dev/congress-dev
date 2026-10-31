import asyncio
import base64
import json
from typing import List, Optional, Tuple

import chromadb
from chromadb.config import Settings

from congress_fastapi.handlers.uscode import chroma_host
from congress_fastapi.models.legislation.text_search import (
    MAX_RESULT_WINDOW,
    BillTextHit,
    BillTextSearchRequest,
    BillTextSearchResponse,
)
from congress_parser.bill_documents import bill_label
from congress_parser.embeddings import embed_texts

COLLECTION_NAME = "legislation"


def encode_cursor(offset: int) -> str:
    return base64.urlsafe_b64encode(json.dumps({"o": offset}).encode()).decode()


def decode_cursor(cursor: Optional[str]) -> int:
    if not cursor:
        return 0
    try:
        offset = int(json.loads(base64.urlsafe_b64decode(cursor.encode()))["o"])
    except Exception:
        raise ValueError("Invalid cursor")
    if offset < 0:
        raise ValueError("Invalid cursor")
    return offset


def build_where(req: BillTextSearchRequest) -> Optional[dict]:
    clauses = []
    if req.congress is not None:
        clauses.append({"congress": req.congress})
    if req.chamber:
        clauses.append({"chamber": req.chamber.capitalize()})
    if req.bill_type:
        clauses.append({"bill_type": req.bill_type.lower().replace(".", "")})
    if req.number is not None:
        clauses.append({"number": req.number})
    if req.version:
        clauses.append({"version": req.version.upper()})
    if req.legislation_id is not None:
        clauses.append({"legislation_id": req.legislation_id})
    if req.legislation_version_id is not None:
        clauses.append({"legislation_version_id": req.legislation_version_id})
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def make_snippet(document: str, max_chars: int) -> Tuple[str, bool]:
    """Drop the context header line and trim to ``max_chars`` on a word boundary."""
    _, _, body = document.partition("\n")
    body = (body or document).strip()
    if len(body) <= max_chars:
        return body, False
    cut = body[:max_chars].rsplit(" ", 1)[0].rstrip()
    return f"{cut}…", True


def build_hit(meta: dict, document: str, distance: float, max_chars: int) -> BillTextHit:
    snippet, truncated = make_snippet(document, max_chars)
    section = meta.get("section_display", "")
    label = bill_label(
        meta["chamber"], _type_name(meta["bill_type"]), meta["number"], meta["congress"]
    )
    citation = f"{label} {meta['version']}"
    if section:
        citation += f" § {section.rstrip('.')}"
    return BillTextHit(
        citation=citation,
        score=round(1.0 - distance, 4),
        legislation_id=meta["legislation_id"],
        legislation_version_id=meta["legislation_version_id"],
        legislation_content_id=meta["legislation_content_id"],
        lc_ident=meta.get("lc_ident") or None,
        congress=meta["congress"],
        chamber=meta["chamber"],
        bill_type=meta["bill_type"],
        number=meta["number"],
        version=meta["version"],
        bill_title=meta.get("bill_title", ""),
        section_display=section,
        heading=meta.get("heading", ""),
        snippet=snippet,
        snippet_truncated=truncated,
        chunk_index=meta["chunk_index"],
        chunk_count=meta["chunk_count"],
    )


_CODE_TO_TYPE = {
    "hr": "Bill", "s": "Bill", "hjres": "JRes", "sjres": "JRes",
    "hconres": "CRes", "sconres": "CRes", "hres": "Res", "sres": "Res",
}


def _type_name(bill_type_code: str) -> str:
    return _CODE_TO_TYPE.get(bill_type_code, "Bill")


async def search_bill_text(req: BillTextSearchRequest) -> BillTextSearchResponse:
    offset = decode_cursor(req.cursor)
    window = offset + req.limit
    if window > MAX_RESULT_WINDOW:
        raise ValueError(
            f"Results are limited to the top {MAX_RESULT_WINDOW}; refine the query or filters"
        )

    query_vector = (await asyncio.to_thread(embed_texts, [req.query]))[0]
    client = await chromadb.AsyncHttpClient(
        host=chroma_host,
        port=8000,
        ssl=False,
        headers=None,
        settings=Settings(),
        tenant="congress-dev",
        database="usc-chat",
    )
    collection = await client.get_collection(COLLECTION_NAME, embedding_function=None)
    # Fetch one extra to know whether another page exists.
    response = await collection.query(
        query_embeddings=[query_vector],
        n_results=window + 1,
        where=build_where(req),
        include=["metadatas", "documents", "distances"],
    )
    metas = response["metadatas"][0]
    docs = response["documents"][0]
    dists = response["distances"][0]

    page = list(zip(metas, docs, dists))[offset:window]
    has_more = len(metas) > window and window < MAX_RESULT_WINDOW
    hits: List[BillTextHit] = [
        build_hit(m, d, dist, req.max_snippet_chars) for m, d, dist in page
    ]
    return BillTextSearchResponse(
        hits=hits, next_cursor=encode_cursor(window) if has_more else None
    )
