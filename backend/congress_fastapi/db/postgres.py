import os

from databases import Database

DATABASE_URL = f"postgresql://{os.getenv('db_user')}:{os.getenv('db_pass')}@{os.getenv('db_host')}/{os.getenv('db_table')}"

database = None


async def get_database() -> Database:
    """
    Connects to Postgres and returns a database object
    """
    print(f"Connecting to {DATABASE_URL}")
    global database
    if database is None:
        database = Database(DATABASE_URL)
        await database.connect()
    return database
