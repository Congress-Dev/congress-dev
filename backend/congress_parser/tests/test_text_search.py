import pytest

pytest.importorskip("chromadb")

from congress_fastapi.handlers.legislation.text_search import (  # noqa: E402
    build_hit,
    build_where,
    decode_cursor,
    encode_cursor,
    make_snippet,
)
from congress_fastapi.models.legislation.text_search import (  # noqa: E402
    BillTextSearchRequest,
)


def test_cursor_roundtrip_and_invalid():
    assert decode_cursor(None) == 0
    assert decode_cursor(encode_cursor(30)) == 30
    with pytest.raises(ValueError):
        decode_cursor("not-a-cursor")


def test_where_combines_filters():
    assert build_where(BillTextSearchRequest(query="x")) is None
    assert build_where(BillTextSearchRequest(query="x", congress=118)) == {"congress": 118}
    where = build_where(
        BillTextSearchRequest(query="x", congress=118, chamber="house", bill_type="H.R.", version="ih")
    )
    assert where == {
        "$and": [
            {"congress": 118},
            {"chamber": "House"},
            {"bill_type": "hr"},
            {"version": "IH"},
        ]
    }


def test_snippet_drops_header_and_trims_on_word_boundary():
    doc = "H.R. 1 (118th Congress) IH — Title\n" + "alpha beta gamma " * 100
    snippet, truncated = make_snippet(doc, 50)
    assert truncated and snippet.endswith("…") and len(snippet) <= 51
    assert "Congress" not in snippet
    assert make_snippet("hdr\nshort", 50) == ("short", False)


def test_build_hit_citation():
    meta = {
        "legislation_id": 1, "legislation_version_id": 2, "legislation_content_id": 3,
        "lc_ident": "s2", "congress": 118, "chamber": "House", "bill_type": "hr",
        "number": 1234, "version": "IH", "bill_title": "A bill",
        "section_display": "SEC. 2.", "heading": "Loans", "chunk_index": 0, "chunk_count": 1,
    }
    hit = build_hit(meta, "hdr\nbody text", 0.25, 200)
    assert hit.citation == "H.R. 1234 (118th Congress) IH § SEC. 2"
    assert hit.score == 0.75
