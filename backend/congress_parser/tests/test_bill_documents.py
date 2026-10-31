from congress_parser.bill_documents import (
    bill_label,
    bill_type_code,
    build_document,
    build_section_chunks,
)


def row(cid, parent, order, ctype, display=None, heading=None, content=None, ident=None):
    return {
        "legislation_content_id": cid,
        "parent_id": parent,
        "order_number": order,
        "content_type": ctype,
        "section_display": display,
        "heading": heading,
        "content_str": content,
        "lc_ident": ident,
    }


ROWS = [
    row(1, None, 0, "legis-body"),
    row(2, 1, 0, "section", "SEC. 1.", "Short title", "This Act may be cited as the X Act.", "s1"),
    row(3, 1, 1, "section", "SEC. 2.", "Loans", "The Administrator shall make loans.", "s2"),
    row(4, 3, 0, "subsection", "(a)", None, "Small businesses are eligible.", "s2a"),
    # quoted section nested inside another section must not become its own unit
    row(5, 4, 0, "section", "SEC. 99.", "Quoted", "Quoted text.", "q99"),
]


def test_units_are_outermost_sections():
    chunks = build_section_chunks(ROWS)
    assert [c.lc_ident for c in chunks] == ["s1", "s2"]
    assert "Small businesses are eligible." in chunks[1].text
    assert "Quoted text." in chunks[1].text


def test_long_section_is_split_with_indices():
    big = row(10, 1, 0, "section", "SEC. 3.", "Big", None, "s3")
    kids = [row(11 + i, 10, i, "paragraph", f"({i})", None, "word " * 100) for i in range(6)]
    chunks = build_section_chunks([ROWS[0], big] + kids, max_chunk_chars=1000)
    assert len(chunks) > 1
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))
    assert all(c.chunk_count == len(chunks) for c in chunks)
    assert all(len(c.text) <= 1000 for c in chunks)


def test_fallback_when_no_sections():
    rows = [
        row(1, None, 0, "legis-body"),
        row(2, 1, 0, "resolution-text", None, None, "Resolved, that things happen."),
    ]
    chunks = build_section_chunks(rows)
    assert len(chunks) == 1 and "things happen" in chunks[0].text


def test_empty_sections_skipped():
    assert build_section_chunks([ROWS[0], row(2, 1, 0, "section", None, None, None)]) == []


def test_document_header_and_labels():
    chunk = build_section_chunks(ROWS)[1]
    doc = build_document(bill_label("House", "Bill", 1234, 118) + " IH", "A bill", chunk)
    assert doc.startswith("H.R. 1234 (118th Congress) IH — A bill — SEC. 2. Loans\n")
    assert bill_label("Senate", "JRes", 5, 111) == "S.J.Res. 5 (111th Congress)"
    assert bill_label("Senate", "Res", 5, 102) == "S.Res. 5 (102nd Congress)"
    assert bill_type_code("House", "CRes") == "hconres"
