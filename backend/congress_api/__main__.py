#!/usr/bin/env python3

import os

import connexion
from flask_compress import Compress
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy_session import current_session, flask_scoped_session
from sqlalchemy.orm import sessionmaker

from billparser.db.handler import DATABASE_URI
from congress_api import encoder

CACHE_HEADER_TIME = int(os.environ.get("CACHE_HEADER_TIME", 0))
app = connexion.App(__name__, specification_dir="./openapi/")


@app.app.after_request
def add_header(response):
    if CACHE_HEADER_TIME > 0:
        response.cache_control.max_age = CACHE_HEADER_TIME
    return response


def main():
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api(
        "openapi.yaml", arguments={"title": "Congress.Dev API"}, pythonic_params=True
    )
    app.app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db = SQLAlchemy(app.app)
    CORS(app.app, resources={r"*": {"origins": "*"}})
    Compress(app.app)
    session_factory = sessionmaker(bind=db.engine)
    session = flask_scoped_session(session_factory, app.app)
    app.run(port=9090, debug=True)


if __name__ == "__main__":
    main()
