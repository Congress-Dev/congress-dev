import json
import logging
import logging.handlers
import os
import platform
import ssl
import time
from collections import defaultdict
from functools import lru_cache
from time import strftime

import connexion
from flask import request
from flask_compress import Compress
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import flask_scoped_session
from flask_sqlalchemy_session import current_session
from sqlalchemy.orm import sessionmaker

from billparser.db.handler import DATABASE_URI
from billparser.db.queries import (
    get_bill_contents,
    get_bill_metadata,
    get_bills,
    get_chapters,
    get_content,
    get_content_versions,
    get_diffs,
    get_latest_content,
    get_latest_sections,
    get_sections,
    get_versions,
    get_revisions,
    get_revision_diff,
    get_latest_base
)
from billparser.db.models import (
    USCChapter,
    USCSection,
    USCContent,
    USCContentDiff,
    Version,
    Legislation,
    LegislationVersion,
    LegislationContent,
)
from billparser.helpers import treeify

windows = platform.system() == "Windows"

PORT = int(os.environ.get("PORT", "9090"))
COMPRESS_MIMETYPES = [
    "text/html",
    "text/css",
    "text/xml",
    "application/json",
    "application/javascript",
]
COMPRESS_LEVEL = 6
COMPRESS_MIN_SIZE = 500
HAVE_CERT = os.environ.get("HAS_CERT", "false").lower() == "true"
if not windows and HAVE_CERT:
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(
        "/etc/letsencrypt/live/congress.dev/fullchain.pem",
        "/etc/letsencrypt/live/congress.dev/privkey.pem",
    )
os.makedirs("/var/log/uscode/", exist_ok=True)
LOG_FILENAME = "/var/log/uscode/access.log"

access_logger = logging.getLogger("MyLogger")
access_logger.setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME, maxBytes=1024 * 1024 * 10, backupCount=1000
)

access_logger.addHandler(handler)

app = connexion.FlaskApp(__name__)
app.app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app.app)
CORS(app.app, resources={r"*": {"origins": "*"}})
Compress(app.app)
session_factory = sessionmaker(bind=db.engine)
session = flask_scoped_session(session_factory, app.app)

row2dict = lambda r: {c.name: str(getattr(r, c.name)) for c in r.__table__.columns}


@app.route("/bills", methods=["GET"])
def bills() -> str:
    """
    This is the bill search function. There are a few query parameters:
    Params:
        h (int): Boolean of if they requested House bills
        s (int): Boolean of if they requested Senate bills
        q (str): Text to search for

        These are kinda dumb.
        incl (str): Mutually exclusive search for specific bill version types (include)
        decl (str): Mutually exclusive search for specific bill version types (exclude)
    Returns:
        str: Array of objects representing the bills that match the search
    """
    house = request.args.get("h", default=1, type=int)
    senate = request.args.get("s", default=1, type=int)
    query = request.args.get("q", default="", type=str)
    incl = request.args.get("incl", default="", type=str)
    decl = request.args.get("decl", default="", type=str)
    start = time.time()
    bill_by_number = defaultdict(lambda: {})
    for bill in get_bills(house, senate, query, incl, decl):
        title = "{}-{}".format(bill.chamber.value[0], bill.number)
        #obj = row2dict(bill)
        obj = bill.to_dict()
        obj["versions"] = [
            x.to_dict()
            for x in bill.versions
            if (
                True
                or (  # Filter based on only the included versions?
                    incl == "" and decl == ""
                )
                or (incl != "" and x.legislation_version in incl.split(","))
                or (decl != "" and x.legislation_version in decl.split(","))
            )
        ]
        bill_by_number[title] = obj
    res = json.dumps(bill_by_number)
    end = time.time()
    print("Took", end - start)
    return res


@app.route("/bill/<string:bill_version>", methods=["GET"])
def bill_content(bill_version: str) -> str:
    """
    Returns the bill text, broken down by the way the XML was structured

    Args:
        bill_version (str): bill_version_id used as a fk on the BillContent table

    Returns:
        str: String json array of bills
    """
    results = get_bill_contents(bill_version)
    results = [x.to_dict() for x in results]
    return json.dumps(results)


@app.route("/bill_tree/<string:bill_version>", methods=["GET"])
def bill_content_tree(bill_version: str) -> str:
    """
    Handles assembling the bill tree for a particular bill

    Args:
        bill_version (str): bill_version_id used as a fk on the BillContent table

    Returns:
        str: A treeified version of the bill, and the associated metadata
    """
    results = get_bill_contents(bill_version)
    results = [x.to_dict() for x in results]
    metadata = get_bill_metadata(bill_version)
    res = treeify(results)["child"][0]
    return json.dumps({"content": res, "metadata": metadata})


@app.route("/titles", methods=["GET"])
def titles() -> str:
    """
    Returns all the chapters of the USCode

    Returns:
        str: str array of the chapter objects
    """
    res = [chapter.to_dict() for chapter in get_chapters()]
    return json.dumps(res)


@app.route("/versions", methods=["GET"])
def versions() -> str:
    """
    More of a debug function that lists all the Version rows
    These represent the different USCode release points, and the bills themselves

    Returns:
        str: Dump of the Version table
    """
    res = []
    for version in get_versions():
        res.append(version.to_dict())
    return json.dumps(res)


@app.route("/revisions", methods=["GET"])
def revisions() -> str:
    """
    Returns a dump of the USCode release points available in the database.
    These are the XML dumps that are put out when an enrolled bill is codified.

    Returns:
        str: Dump of the Version table where base_id == None
    """
    res = []
    for version in get_revisions():
        res.append(version.to_dict())
    return json.dumps(res)


@app.route("/version", methods=["POST"])
def version() -> str:
    """
    Grabs the diff for a specific bill_version_id.
    ContentDiff is a preprocessed table with all the diffs, this merely returns them.

    Currently the entire set is returned.

    Returns:
        str: Object with the diffs and the contents enumerated for a specific bill version
    """
    req = request.json
    res = {"diffs": [], "contents": []}
    if "version" in req:
        for diff in get_diffs(int(req["version"])):
            res["diffs"].append(diff.to_dict())
        for content in get_content_versions(int(req["version"])):
            res["contents"].append(content.to_dict())
    return json.dumps(res)


@app.route("/latest/chapter/<string:chapter_number>", methods=["GET"])
def latest_sections(chapter_number: str) -> str:
    """
    Returns the sections for a given chapter in the latest version of the USCode

    # TODO: Paginate
    Currently not paginated, might also be useless to return them all, as a user likely
    wants a specific one, and it's sort of unintelligble to look at them all at once.


    Args:
        chapter_number (str): Chapter "Number" which is actually not a number,
            It's more of the Chapter's official "number", all pulled from the uscode.house.gov
            05, 11, 18, 28, 50 all have *A varients.

    Returns:
        str: Stringified array of the rows
    """
    res = []
    for section in get_latest_sections(chapter_number):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route("/chapter/<int:chapter_id>", methods=["GET"])
def sections(chapter_id: int) -> str:
    """
    Gets the sections for a specific chapter id.

    # TODO: Unused function?

    Args:
        chapter_id (int): PK on the Chapter table

    Returns:
        str: Stringifed array of the rows
    """
    latest_base = get_latest_base()

    res = []
    for section in get_sections(str(chapter_id), latest_base.version_id):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route(
    "/latest/section/<string:chapter_number>/<string:section_number>", methods=["GET"]
)
def latest_contents(chapter_number: str, section_number: str) ->  str:
    """
    Grabs the content for a given section inside a given chapter.

    # TODO: Create a typevar for chapter_number

    Args:
        chapter_number (str): Chapter "Number" which is actually not a number,
            It's more of the Chapter's official "number", all pulled from the uscode.house.gov
            05, 11, 18, 28, 50 all have *A varients.
        section_number (str): Section "Number" basically the same as above, they are not really numbers

    Returns:
        str: Stringifed array of the rows
    """
    res = []
    for section in get_latest_content(chapter_number, section_number):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route("/section/<int:section_id>", methods=["GET"])
def contents(section_id: int) -> str:
    """
    Returns the data for a given section_id

    Args:
        section_id (int): PK on the Section table

    Returns:
        str: Stringified array of the content rows
    """
    latest_base = get_latest_base()
    res = []
    for section in get_content(str(section_id), latest_base.version_id):
        res.append(section.to_dict())
    return json.dumps(res)


@app.app.after_request
def add_header(response):
    """
    This was something I was doing for logging requests for a goaccess endpoint which isn't used anymore
    """
    if not windows:
        if "X-Real-Ip" in request.headers:
            remote_addr = request.headers.getlist("X-Real-Ip")[0].strip()
        else:
            remote_addr = request.remote_addr or "untrackable"
        ts = strftime("[%d/%b/%Y:%k:%M:%S %z]")
        log_message = f'{remote_addr} - - {ts} "{request.method} {request.full_path} HTTP/1.1" {response.status_code} {response.content_length}'
        access_logger.info(log_message)
        response.cache_control.max_age = 60
    return response


if __name__ == "__main__":
    if not windows and HAVE_CERT:
        app.run(
            host="localhost",
            port=PORT,
            debug=False,
            ssl_context=context,
            server="gevent",
        )
    else:
        print("Starting")
        app.run(host="0.0.0.0", port=PORT, debug=False)
