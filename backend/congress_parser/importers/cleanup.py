from sqlalchemy import select, func
from sqlalchemy.orm import aliased
import os

from congress_db.session import engine, Session
from congress_db.models import USCRelease

webhook_url = os.environ.get("DISCORD_WEBHOOK", None)

query = """SELECT *
FROM   (SELECT legislation.legislation_id,
               chamber,
               "number",
               lv.legislation_version,
               Count(lc.legislation_content_id) AS items,
               congress_id
        FROM   PUBLIC.legislation
               LEFT JOIN legislation_version AS lv
                      ON lv.legislation_id = legislation.legislation_id
               LEFT JOIN legislation_content AS lc
                      ON lv.legislation_version_id = lc.legislation_version_id
        GROUP  BY legislation.legislation_id,
                  chamber,
                  "number",
                  legislation_version,
                  congress_id) AS t
WHERE  t.items = 0;
"""


def send_message(text):
    if webhook_url is not None:
        import requests

        requests.post(webhook_url, json={"content": text})

def cleanup_usc_release(session):
    # Step 1: Identify duplicates
    subquery = (
        session.query(
            USCRelease.short_title,
            USCRelease.effective_date,
            func.max(USCRelease.created_at).label("latest_created_at"),
            func.count(USCRelease.usc_release_id).label("duplicate_count")
        )
        .group_by(USCRelease.short_title, USCRelease.effective_date)
        .having(func.count(USCRelease.usc_release_id) > 1)
        .subquery()
    )

    # Step 2: Join to find the rows to delete
    duplicate_alias = aliased(USCRelease)
    rows_to_delete = (
        session.query(duplicate_alias)
        .join(
            subquery,
            (duplicate_alias.short_title == subquery.c.short_title)
            & (duplicate_alias.effective_date == subquery.c.effective_date)
            & (duplicate_alias.created_at == subquery.c.latest_created_at)
        )
    )

    for row in rows_to_delete:
        print(row.usc_release_id)
        send_message(
            f"Removing duplicate USCRelease {row.usc_release_id}"
        )

        session.delete(row)
        session.commit()

def cleanup_legislation():
    # For some reason, we get bills that produce nothing
    result = list(engine.execute(query))
    print(len(result), "bills created no rows")

    if(len(result) > 0):
        send_message(
            f"Removing {len(result)} bills for no content.\nExamples: {', '.join([f'{x[1]}-{x[2]}-{x[3]}' for x in result[:5]])}"
        )
        for row in result:
            legislation_id = row[0]
            engine.execute(
                f"DELETE FROM legislation WHERE legislation_id = {legislation_id}"
            )

if __name__ == "__main__":
    session = Session()

    # cleanup_legislation()
    cleanup_usc_release(session)
