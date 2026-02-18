import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

username = os.environ.get("db_user", "parser")
password = os.environ.get("db_pass", "parser")
table = os.environ.get("db_table", "us_code_2025")
db_host = os.environ.get("db_host", "0.0.0.0:5432")

# Per-worker connection pool bounds.  Each parallel worker process gets its own
# pool; total DB connections ≤ PARSE_THREADS * (DB_POOL_SIZE + DB_MAX_OVERFLOW).
# With the default of 2+3=5 per worker and ≤16 workers that stays well under
# PostgreSQL's default max_connections=100.
DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", 2))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", 3))

DATABASE_URI = f"postgresql://{username}:{password}@{db_host}/{table}"
engine = create_engine(
    DATABASE_URI,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    connect_args={"sslmode": "disable"},
)

Session = scoped_session(sessionmaker(bind=engine))

# Guard so init_session() creates a new engine at most once per worker process.
_worker_engine = None


def init_session():
    """Initialize a bounded connection pool for the current worker process.

    Called at the top of every parse_bill() invocation.  The _worker_engine
    guard ensures we only create the engine once per process so that pool
    connections are reused across bills handled by the same worker rather than
    a brand-new (unbounded) engine being created for every bill.
    """
    global Session, _worker_engine
    if _worker_engine is not None:
        return
    _worker_engine = create_engine(
        DATABASE_URI,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        connect_args={"sslmode": "disable"},
    )
    Session = scoped_session(sessionmaker(bind=_worker_engine))


def get_scoped_session():
    """Return a new session using a fresh, bounded engine."""
    global Session
    _engine = create_engine(
        DATABASE_URI,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
        pool_pre_ping=True,
        connect_args={"sslmode": "disable"},
    )
    Session = scoped_session(sessionmaker(bind=_engine))
    return Session()

