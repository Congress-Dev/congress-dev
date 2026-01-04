from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
from collections import defaultdict

import pandas
import requests
from lxml import etree


from congress_db.models import USCPopularName, USCActSection, USCRelease
from congress_db.session import Session


popoular_name_url = "https://uscode.house.gov/popularnames/popularnames.htm"
table3_zip_url = "https://uscode.house.gov/table3/table3-xml-bulk.zip"


def get_popular_names():
    print("Downloading Popular Name List")
    popular_names = requests.get(popoular_name_url)

    print("Downloaded popularnames.htm", len(popular_names.content), "bytes")
    parser = etree.HTMLParser(huge_tree=True)
    tree = etree.parse(BytesIO(popular_names.content), parser)

    items = tree.xpath("//div[@class='popular-name-table-entry']")

    print("Detected", len(items), "acts")

    res = [
        {
            "Name": item.getchildren()[0].text,
            "PubL": item.getchildren()[1].getchildren()[0].text,
        }
        for item in items
        if len(item.getchildren()) > 1 and item.getchildren()[1].text == "Pub. L. "
    ]

    print("Detected", len(res), "PubL acts")
    return res


def get_table_3():
    table3 = requests.get(table3_zip_url)
    print("Downloaded table3-xml-bulk.zip", len(table3.content), "bytes")
    with ZipFile(BytesIO(table3.content), "r") as table3_zip:
        with table3_zip.open(table3_zip.namelist()[0]) as table3_xml:
            t3edit = etree.fromstring(table3_xml.read())
            rec = []
            acts = t3edit.xpath("//act")

            print("Detected", len(acts), "acts")
            for act in acts:
                act_base = {f"act_{key}": value for key, value in act.attrib.items()}
                act_children = act.getchildren()
                if act_children[0].tag != "num":
                    print("Detected Act without num", act_base["act_id"])
                else:
                    act_base["act_num"] = act_children[0].text
                    act_records = act.xpath("record")
                    for record in act_records:
                        rec.append(
                            {
                                **act_base,
                                **{
                                    f"record_{key}": value
                                    for key, value in record.attrib.items()
                                },
                                **{
                                    f"record_{item.tag}": item.text
                                    for item in record.getchildren()
                                },
                            }
                        )

            return rec


if __name__ == "__main__":
    session: "SQLAlchemy.Session" = Session()
    popular_name_objs = get_popular_names()
    table_3_objs = get_table_3()

    latest_release: USCRelease = session.query(USCRelease).order_by(
        USCRelease.effective_date.desc()
    ).limit(1).all()
    if latest_release is not None and len(latest_release) > 0:
        print("Latest release is", latest_release[0].short_title)
        pop_models = [
            USCPopularName(
                name=obj["Name"],
                public_law_number=obj["PubL"],
                act_date=datetime(2000, 1, 1),  # TODO: I'm lazy
                act_congress=int(obj["PubL"].split("-")[0]),
                usc_release_id=latest_release[0].usc_release_id,
            )
            for obj in popular_name_objs
        ]
        pop_models_by_publ = defaultdict(list)
        for mod in pop_models:
            session.add(mod)
            pop_models_by_publ[mod.public_law_number].append(mod)

        for t_obj in table_3_objs:
            for pop_model in pop_models_by_publ.get(t_obj.get("act_num"), []):
                session.add(
                    USCActSection(
                        act_section=t_obj.get("record_act-section"),
                        usc_title=t_obj.get("record_united-states-code-title"),
                        usc_section=t_obj.get("record_united-states-code-section"),
                        usc_popular_name_id=pop_model.usc_popular_name_id,
                    )
                )
                pop_model.act_date = datetime(*[int(x) for x in t_obj.get("act_date").split("-")])
        print("Added", len(pop_models))
        session.flush()
        session.commit()

