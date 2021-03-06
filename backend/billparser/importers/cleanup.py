from billparser.db.handler import engine
import os

webhook_url = os.environ.get("DISCORD_WEBHOOK", None)

query = """SELECT *
FROM   (SELECT legislation.legislation_id,
               chamber,
               "number",
               lv.legislation_version,
               Count(lc.legislation_content_id) AS items
        FROM   PUBLIC.legislation
               LEFT JOIN legislation_version AS lv
                      ON lv.legislation_id = legislation.legislation_id
               LEFT JOIN legislation_content AS lc
                      ON lv.legislation_version_id = lc.legislation_version_id
        GROUP  BY legislation.legislation_id,
                  chamber,
                  "number",
                  legislation_version) AS t
WHERE  t.items = 0; 
"""


def send_message(text):
    if webhook_url is not None:
        import requests

        requests.post(webhook_url, json={"content": text})


if __name__ == "__main__":
    # For some reason, we get bills that produce nothing
    result = list(engine.execute(query))
    print(len(result), "bills created no rows")
    send_message(
        f"Removing {len(result)} bills for no content.\nExamples: {', '.join([f'{x[1]}-{x[2]}-{x[3]}' for x in result[:5]])}"
    )
    for row in result:
        legislation_id = row[0]
        # engine.execute(
        #     f"DELETE FROM legislation WHERE legislation_id = {legislation_id}"
        # )
