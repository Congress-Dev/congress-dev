import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

username = os.environ.get("db_user", "parser")
password = os.environ.get("db_pass", "parser")
table = os.environ.get("db_table", "us_code_2025")
db_host = os.environ.get("db_host", "0.0.0.0:5432")

DATABASE_URI = f"postgresql://{username}:{password}@{db_host}/{table}"
engine = create_engine(
    DATABASE_URI, poolclass=NullPool, connect_args={"sslmode": "disable"}
)

Session = scoped_session(sessionmaker(bind=engine))

def init_session():
    """Initialize the Session object in the current process."""
    global Session
    engine = create_engine(
        DATABASE_URI, poolclass=NullPool, connect_args={"sslmode": "disable"}
    )
    engine.dispose()
    Session = scoped_session(sessionmaker(bind=engine))


def get_scoped_session():
    """Initialize the Session object in the current process."""
    global Session
    engine = create_engine(
        DATABASE_URI, poolclass=NullPool, connect_args={"sslmode": "disable"}
    )
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

