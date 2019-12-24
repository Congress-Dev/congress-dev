from billparser.db.models import Bill, BillVersion, Version, ContentDiff
from billparser.transformer import Session


def run_prune():
    # This is removing any bills that I was unable to generate differences for
    # The thought behind this is that they stay in the list, but they don't show anything
    # So they distract from the functionality of the site
    session = Session()
    boys = session.query(ContentDiff.version_id).distinct(ContentDiff.version_id).all()
    session.execute("ALTER TABLE version DISABLE TRIGGER ALL;")
    session.query(Version).filter(Version.version_id.notin_(boys)).filter(
        Version.base_id.isnot(None)
    ).delete(synchronize_session=False)
    session.execute("ALTER TABLE version ENABLE TRIGGER ALL;")
    session.commit()
    session.execute("ALTER TABLE bill_version DISABLE TRIGGER ALL;")
    session.query(BillVersion).filter(BillVersion.bill_version_id.notin_(boys)).delete(
        synchronize_session=False
    )
    session.execute("ALTER TABLE bill_version ENABLE TRIGGER ALL;")
    session.commit()


if __name__ == "__main__":
    run_prune()
