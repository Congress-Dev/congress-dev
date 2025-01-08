from billparser.bioguide.manager import BioGuideImporter


if __name__ == "__main__":
    """
    Run the bioguide importer from the zip
    """
    BioGuideImporter().download_to_database()