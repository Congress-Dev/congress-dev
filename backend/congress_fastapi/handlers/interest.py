from typing import List

from sqlalchemy import select, insert, update, or_, func

from congress_fastapi.db.postgres import get_database
from congress_fastapi.handlers.uscode import search_chroma
from congress_db.models import (
    UserInterest,
    UserInterestUscContent,
    USCContent,
    USCContentDiff,
    LegislationVersion,
    Legislation,
    Congress,
)


async def handle_get_interest(user_id: str) -> dict:
    database = await get_database()

    interest = await database.fetch_one(
        select(UserInterest).where(UserInterest.user_id == user_id)
    )
    if not interest:
        return {"interest": None, "matches": []}

    matches = await database.fetch_all(
        select(UserInterestUscContent)
        .where(
            UserInterestUscContent.user_interest_id
            == interest["user_interest_id"]
        )
        .order_by(UserInterestUscContent.match_rank)
    )
    return {
        "interest": dict(interest),
        "matches": [dict(m) for m in matches],
    }


async def handle_save_interest(user_id: str, interest_text: str) -> dict:
    database = await get_database()

    existing = await database.fetch_one(
        select(UserInterest).where(UserInterest.user_id == user_id)
    )
    if existing:
        await database.execute(
            update(UserInterest)
            .where(UserInterest.user_id == user_id)
            .values(interest_text=interest_text, updated_at=func.now())
        )
        interest_id = existing["user_interest_id"]
    else:
        interest_id = await database.execute(
            insert(UserInterest).values(
                user_id=user_id, interest_text=interest_text
            )
        )

    # Run ChromaDB semantic search
    try:
        chroma_matches = await search_chroma(interest_text, 50)
    except Exception:
        chroma_matches = []

    # Deactivate all previous auto-matched sections
    await database.execute(
        update(UserInterestUscContent)
        .where(
            UserInterestUscContent.user_interest_id == interest_id
        )
        .where(UserInterestUscContent.match_source == "auto")
        .values(is_active=False)
    )

    # Upsert new auto-matched sections
    for rank, match in enumerate(chroma_matches):
        usc_ident = match.get("usc_ident")
        if not usc_ident:
            continue

        existing_match = await database.fetch_one(
            select(UserInterestUscContent)
            .where(
                UserInterestUscContent.user_interest_id == interest_id
            )
            .where(UserInterestUscContent.usc_ident == usc_ident)
        )
        if existing_match:
            await database.execute(
                update(UserInterestUscContent)
                .where(
                    UserInterestUscContent.user_interest_usc_content_id
                    == existing_match["user_interest_usc_content_id"]
                )
                .values(is_active=True, match_rank=rank, match_source="auto")
            )
        else:
            await database.execute(
                insert(UserInterestUscContent).values(
                    user_interest_id=interest_id,
                    usc_ident=usc_ident,
                    match_source="auto",
                    is_active=True,
                    match_rank=rank,
                )
            )

    return await handle_get_interest(user_id)


async def handle_toggle_interest_section(
    user_id: str, usc_ident: str, is_active: bool
) -> None:
    database = await get_database()

    interest = await database.fetch_one(
        select(UserInterest).where(UserInterest.user_id == user_id)
    )
    if not interest:
        return

    await database.execute(
        update(UserInterestUscContent)
        .where(
            UserInterestUscContent.user_interest_id
            == interest["user_interest_id"]
        )
        .where(UserInterestUscContent.usc_ident == usc_ident)
        .values(is_active=is_active)
    )


async def handle_add_interest_section(user_id: str, usc_ident: str) -> None:
    database = await get_database()

    interest = await database.fetch_one(
        select(UserInterest).where(UserInterest.user_id == user_id)
    )
    if not interest:
        return

    existing = await database.fetch_one(
        select(UserInterestUscContent)
        .where(
            UserInterestUscContent.user_interest_id
            == interest["user_interest_id"]
        )
        .where(UserInterestUscContent.usc_ident == usc_ident)
    )
    if existing:
        await database.execute(
            update(UserInterestUscContent)
            .where(
                UserInterestUscContent.user_interest_usc_content_id
                == existing["user_interest_usc_content_id"]
            )
            .values(is_active=True, match_source="manual")
        )
    else:
        await database.execute(
            insert(UserInterestUscContent).values(
                user_interest_id=interest["user_interest_id"],
                usc_ident=usc_ident,
                match_source="manual",
                is_active=True,
                match_rank=None,
            )
        )


async def handle_get_interest_legislation(user_id: str) -> dict:
    database = await get_database()

    interest = await database.fetch_one(
        select(UserInterest).where(UserInterest.user_id == user_id)
    )
    if not interest:
        return {"legislation": []}

    match_rows = await database.fetch_all(
        select(UserInterestUscContent.usc_ident)
        .where(
            UserInterestUscContent.user_interest_id
            == interest["user_interest_id"]
        )
        .where(UserInterestUscContent.is_active == True)  # noqa: E712
        .distinct()
    )
    idents: List[str] = [r["usc_ident"] for r in match_rows if r["usc_ident"]]
    if not idents:
        return {"legislation": []}

    query = (
        select(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
            func.min(LegislationVersion.effective_date).label("effective_date"),
        )
        .select_from(USCContent)
        .join(
            USCContentDiff,
            USCContentDiff.usc_content_id == USCContent.usc_content_id,
        )
        .join(
            LegislationVersion,
            USCContentDiff.version_id == LegislationVersion.version_id,
        )
        .join(
            Legislation,
            LegislationVersion.legislation_id == Legislation.legislation_id,
        )
        .join(Congress, Congress.congress_id == Legislation.congress_id)
        .where(
            or_(*[USCContent.usc_ident.ilike(f"{ident}%") for ident in idents])
        )
        .group_by(
            Legislation.legislation_id,
            Legislation.title,
            Legislation.number,
            Congress.session_number,
            Legislation.legislation_type,
            Legislation.chamber,
        )
        .order_by(func.min(LegislationVersion.effective_date).desc())
        .limit(100)
    )

    results = await database.fetch_all(query)
    return {"legislation": [dict(r) for r in results]}
