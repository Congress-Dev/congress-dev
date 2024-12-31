import { Breadcrumbs } from "@blueprintjs/core";
import lodash from "lodash";
import { Link, withRouter, useHistory } from "react-router-dom";

import { versionToFull, versionSort } from "common/lookups";

function BillVersionsBreadcrumb({ bill }) {
    const history = useHistory();
    const { legislation_versions = [] } = bill;

    legislation_versions.sort(
        (a, b) =>
            versionSort[
                typeof a === "string"
                    ? a.toLowerCase()
                    : a.legislation_version.toLowerCase()
            ] -
            versionSort[
                typeof b === "string"
                    ? b.toLowerCase()
                    : b.legislation_version.toLowerCase()
            ],
    );

    return (
        <Breadcrumbs
            minVisibleItems={1}
            className="bill-versions"
            breadcrumbRenderer={({ text, link }) => (
                <Link to={link}>{text}</Link>
            )}
            items={lodash.map(legislation_versions, (vers) => {
                return {
                    text: versionToFull[
                        typeof vers === "string"
                            ? vers.toLowerCase()
                            : vers.legislation_version.toLowerCase()
                    ],
                    link: `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers}`,
                    onClick: (e) => {
                        history.push(
                            `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers}`,
                        );
                    },
                };
            })}
        />
    );
}

export default withRouter(BillVersionsBreadcrumb);
