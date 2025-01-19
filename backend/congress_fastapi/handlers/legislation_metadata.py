from typing import List, Optional

from sqlalchemy import select

from billparser.db.models import (
    Appropriation as AppropriationModel,
    Legislation,
    LegislationSponsorship,
    LegislationVersion,
    LegislationVersionEnum,
    LegislationVote,
    Legislator,
    USCRelease,
    Version,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.legislation import (
    LegislationMetadata,
    LegislationVersionMetadata,
    LegislationVoteMetadata,
    LegislatorMetadata,
    Appropriation,
)


async def get_legislation_version_metadata_by_legislation_id(
    legislation_id: int,
) -> Optional[List[LegislationVersionMetadata]]:
    """
    Returns a list of LegislationVersionMetadata objects for a given legislation_id
    """
    database = await get_database()
    query = (
        select(
            *LegislationVersionMetadata.sqlalchemy_columns(),
        ).where(LegislationVersion.legislation_id == legislation_id)
        # .order_by(LegislationVersion.effective_date)
    )
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    print(results)
    return [
        LegislationVersionMetadata.from_sqlalchemy(result)
        for result in results
        if result
    ]


async def get_appropriations_by_legislation_version_id(
    legislation_version_id: int,
) -> List[Appropriation]:
    """
    Returns a list of Appropriation objects for a given legislation_version_id
    """
    database = await get_database()
    query = select(
        *Appropriation.sqlalchemy_columns(),
    ).where(AppropriationModel.legislation_version_id == legislation_version_id)
    results = await database.fetch_all(query)
    result_objs = []
    for result in results:
        try:
            result_objs.append(Appropriation(**result))
        except Exception as e:
            print(result)
            print(e)
    return result_objs


async def get_legislation_metadata_by_legislation_id(
    legislation_id: int, verstion_str: LegislationVersionEnum
) -> Optional[LegislationMetadata]:
    """
    Returns a LegislationMetadata object for a given legislation_id
    """
    database = await get_database()
    query = select(
        *LegislationMetadata.sqlalchemy_columns(),
    ).where(Legislation.legislation_id == legislation_id)
    result = await database.fetch_one(query)
    if result is None:
        return None
    legis_versions = await get_legislation_version_metadata_by_legislation_id(
        legislation_id
    )
    matching_vers = legis_versions[0].legislation_version_id
    for version in legis_versions:
        if version.legislation_version == verstion_str:
            matching_vers = version.legislation_version_id
            break
    # TODO: Right now we only get the first one
    appropriations = await get_appropriations_by_legislation_version_id(matching_vers)
    usc_query = (
        select(USCRelease)
        .join(
            LegislationVersion,
            LegislationVersion.legislation_version_id
            == legis_versions[0].legislation_version_id,
        )
        .join(Version, USCRelease.version_id == Version.base_id)
        .filter(LegislationVersion.version_id == Version.version_id)
    )
    usc_res = await database.fetch_one(usc_query)

    sponsor_query = (
        select(
            *LegislatorMetadata.sqlalchemy_columns(),
            LegislationSponsorship.cosponsor,
        )
        .join(
            LegislationSponsorship,
            LegislationSponsorship.legislator_bioguide_id == Legislator.bioguide_id
        )
        .where(
            LegislationSponsorship.legislation_id == legislation_id
        )
        .group_by(
            Legislator.legislator_id,
            Legislator.bioguide_id,
            LegislationSponsorship.cosponsor
        )
        .order_by(LegislationSponsorship.cosponsor, Legislator.bioguide_id)
    )

    sponsor_result = (await database.fetch_all(sponsor_query));

    sponsor_objs = []
    for sponsor in sponsor_result:
        try:
            sponsor_objs.append(LegislatorMetadata(**sponsor))
        except Exception as e:
            print(result)
            print(e)

    votes_query = (
        select(*LegislationVoteMetadata.sqlalchemy_columns())
        .where(LegislationVote.legislation_id == legislation_id)
        .order_by(LegislationVote.datetime.desc())
    )

    votes_results = (await database.fetch_all(votes_query))

    vote_objs = []
    for vote in votes_results:
        try:
            vote_data = {
                **vote,
                'datetime': vote.datetime.strftime("%Y-%m-%d")
            }

            vote_objs.append(LegislationVoteMetadata(
                **vote_data,
            ))
        except Exception as e:
            print(result)
            print(e)

    usc_release_id = (await database.fetch_one(usc_query)).usc_release_id
    return LegislationMetadata(
        legislation_versions=legis_versions,
        usc_release_id=usc_release_id,
        appropriations=appropriations,
        sponsor=sponsor_objs[0] if len(sponsor_objs) > 0 else None,
        cosponsors=sponsor_objs[1:] if len(sponsor_objs) > 0 else None,
        votes=vote_objs,
        **result,
    )
