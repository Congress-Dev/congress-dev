from billparser.db.models import LegislationChamber, LegislationCommittee
from billparser.db.handler import Session
import yaml
import requests


def fetch_committees_yaml():
    """
    Fetch the current committees YAML from the unitedstates/congress-legislators repository.

    Returns:
        str: YAML string containing committee data

    Raises:
        requests.RequestException: If the request fails
    """
    url = "https://raw.githubusercontent.com/unitedstates/congress-legislators/main/committees-current.yaml"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return response.text


def parse_committee_yaml(yaml_str):
    """
    Parse committee YAML and convert it to a list of dictionaries ready for database insertion.

    Args:
        yaml_str (str): YAML string containing committee data

    Returns:
        list: List of dictionaries representing committees and subcommittees
    """
    committees = []
    yaml_data = yaml.safe_load(yaml_str)

    if not isinstance(yaml_data, list):
        yaml_data = [yaml_data]

    for committee in yaml_data:
        # Determine chamber from type
        chamber = None
        if committee.get("type") == "house":
            chamber = LegislationChamber.House
        elif committee.get("type") == "senate":
            chamber = LegislationChamber.Senate

        committee_dict = {
            "thomas_id": committee.get("thomas_id"),
            "name": committee.get("name"),
            "chamber": chamber,
            "url": committee.get("url"),
            "minority_url": committee.get("minority_url"),
            "committee_id": committee.get(
                "house_committee_id", committee.get("senate_committee_id")
            ),
            "address": committee.get("address"),
            "phone": committee.get("phone"),
            "rss_url": committee.get("rss_url"),
            "jurisdiction": committee.get("jurisdiction"),
            "youtube_id": committee.get("youtube_id"),
            "parent_id": None,  # Main committees have no parent
        }

        # Filter out None values
        committee_dict = {k: v for k, v in committee_dict.items() if v is not None}
        committees.append(committee_dict)

        # Process subcommittees if they exist
        if "subcommittees" in committee and committee["subcommittees"]:
            for subcommittee in committee["subcommittees"]:
                subcommittee_dict = {
                    "thomas_id": subcommittee.get("thomas_id"),
                    "name": subcommittee.get("name"),
                    "chamber": chamber,  # Inherit from parent
                    "address": subcommittee.get("address"),
                    "phone": subcommittee.get("phone"),
                    "parent_id": None,  # This will be filled in after parent is inserted
                }

                # Filter out None values
                subcommittee_dict = {
                    k: v for k, v in subcommittee_dict.items() if v is not None
                }

                # Mark this as needing parent_id assignment
                subcommittee_dict["needs_parent"] = committee["thomas_id"]
                committees.append(subcommittee_dict)

    return committees


def insert_committees_from_yaml(session, yaml_str, congress_id):
    """
    Parse committee YAML and insert into database.

    Args:
        session: SQLAlchemy session
        yaml_str (str): YAML string containing committee data
        congress_id (int): ID of the congress these committees belong to

    Returns:
        list: List of inserted committee objects
    """
    committee_dicts = parse_committee_yaml(yaml_str)

    # Map of thomas_id to committee_id for linking subcommittees to parents
    thomas_id_to_committee = {}
    inserted_committees = []
    thomas_id_to_parent_id = {}
    needs_parent_map = {}
    # First pass: insert all committees without parent relationships
    for committee_dict in committee_dicts:
        needs_parent = committee_dict.pop("needs_parent", None)

        # Add congress_id to all committees
        committee_dict["congress_id"] = congress_id

        committee = LegislationCommittee(**committee_dict)
        session.add(committee)
        session.flush()  # Flush to get the ID

        thomas_id_to_parent_id[committee.thomas_id] = (
            committee.legislation_committee_id
        )
    
        if needs_parent:
            # Remember this committee needs a parent
            needs_parent_map[committee.legislation_committee_id] = needs_parent

        inserted_committees.append(committee)

    # Second pass: update parent_id for subcommittees
    for committee in inserted_committees:
        if needs_parent_map.get(committee.legislation_committee_id):
            parent_thomas_id = needs_parent_map[committee.legislation_committee_id]
            if thomas_id_to_parent_id.get(parent_thomas_id):
                committee.parent_id = thomas_id_to_parent_id[parent_thomas_id]
    
    session.flush()
    print(f"Inserted {len(inserted_committees)} committees")
    return inserted_committees


if __name__ == "__main__":
    session = Session()
    try:
        yaml_str = fetch_committees_yaml()
        insert_committees_from_yaml(session, yaml_str, 1)
        session.commit()
        print("Successfully imported committees from GitHub repository")
    except requests.RequestException as e:
        print(f"Error fetching committees data: {e}")
    except Exception as e:
        print(f"Error importing committees: {e}")
