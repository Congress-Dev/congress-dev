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
    get_revision_diff
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


@app.route("/bills")
def bills():
    house = request.args.get("h", default=1, type=int)
    senate = request.args.get("s", default=1, type=int)
    query = request.args.get("q", default="", type=str)
    incl = request.args.get("incl", default="", type=str)
    decl = request.args.get("decl", default="", type=str)
    start = time.time()
    bill_by_number = defaultdict(lambda: {})
    for bill in get_bills(house, senate, query, incl, decl):
        title = "{}-{}".format(bill.chamber[0], bill.bill_number)
        obj = row2dict(bill)
        obj["versions"] = [
            row2dict(x)
            for x in bill.versions
            if (
                True
                or (  # Filter based on only the included versions?
                    incl == "" and decl == ""
                )
                or (incl != "" and x.bill_version in incl.split(","))
                or (decl != "" and x.bill_version in decl.split(","))
            )
        ]
        bill_by_number[title] = obj
    res = json.dumps(bill_by_number)
    end = time.time()
    print("Took", end - start)
    return res


@app.route("/bill/<string:bill_version>")
def bill_content(bill_version):
    results = get_bill_contents(bill_version)
    results = [x.to_dict() for x in results]
    # print(treeify(results))
    ret_obj = {"contents": results}
    return json.dumps(results)


@app.route("/bill_tree/<string:bill_version>")
def bill_content_tree(bill_version):
    results = get_bill_contents(bill_version)
    results = [x.to_dict() for x in results]
    metadata = get_bill_metadata(bill_version)
    res = treeify(results)["child"][0]
    # ['"`print(res)
    return json.dumps({"content": res, "metadata": metadata})


@app.route("/titles")
def titles():
    res = []
    for chapter in get_chapters():
        res.append(chapter.to_dict())
    return json.dumps(res)


@app.route("/versions")
def versions():
    res = []
    for version in get_versions():
        res.append(version.to_dict())
    return json.dumps(res)


@app.route("/revisions")
def revisions():
    res = []
    for version in get_revisions():
        res.append(version.to_dict())
    return json.dumps(res)

@app.route("/test")
def test():
    return get_revision_diff(1,2)

@app.route("/version", methods=["POST"])
def version():
    print(request)
    req = request.json
    print(req)
    res = {"diffs": [], "contents": []}
    if "version" in req:
        for diff in get_diffs(int(req["version"])):
            res["diffs"].append(diff.to_dict())
        for content in get_content_versions(int(req["version"])):
            res["contents"].append(content.to_dict())
    return json.dumps(res)


@app.route("/latest/chapter/<string:chapter_number>", methods=["GET"])
def latest_sections(chapter_number):
    res = []
    for section in get_latest_sections(chapter_number):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route("/chapter/<int:chapter_id>", methods=["GET"])
def sections(chapter_id):
    latest_base = (
        current_session.query(Version).filter(Version.base_id == None).all()[0]
    )
    res = []
    for section in get_sections(str(chapter_id), latest_base.version_id):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route(
    "/latest/section/<string:chapter_number>/<string:section_number>", methods=["GET"]
)
def latest_contents(chapter_number, section_number):
    res = []
    for section in get_latest_content(chapter_number, section_number):
        res.append(section.to_dict())
    return json.dumps(res)


@app.route("/section/<int:section_id>", methods=["GET"])
def contents(section_id):
    latest_base = (
        current_session.query(Version).filter(Version.base_id == None).all()[0]
    )
    res = []
    for section in get_content(str(section_id), latest_base.version_id):
        res.append(section.to_dict())
    return json.dumps(res)


@app.app.after_request
def add_header(response):
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
