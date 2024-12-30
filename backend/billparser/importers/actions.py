from billparser.actions.parser import parse_bill_for_actions
from billparser.db.queries import get_legislation_version_ids, check_for_action_parses




if __name__ == "__main__":
    """
    Identify which bills need to have they actions parsed
    then parse them
    """
    all_legislation_versions = get_legislation_version_ids()
    action_parse_counts = check_for_action_parses(all_legislation_versions)
    for legislation_version_id, counts in action_parse_counts.items():
        if counts == 0:
            parse_bill_for_actions(legislation_version_id)
