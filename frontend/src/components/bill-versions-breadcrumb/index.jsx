import { Breadcrumbs } from "@blueprintjs/core";
import lodash from "lodash";
import { Link, withRouter, useHistory } from "react-router-dom";

import { versionToFull, versionSort } from "common/lookups";

function BillVersionsBreadcrumb({ bill }) {
    const history = useHistory();
    const { legislation_versions = [] } = bill;

    const versionsNormalized = legislation_versions.map((vers) => {
        return typeof vers === "string"
            ? vers.toLowerCase()
            : vers.legislation_version.toLowerCase();
    });

    versionsNormalized.sort((a, b) => versionSort[a] - versionSort[b]);

    return (
        <Breadcrumbs
            minVisibleItems={1}
            className="bill-versions"
            breadcrumbRenderer={({ text, link }) => (
                <Link to={link}>{text}</Link>
            )}
            items={lodash.map(versionsNormalized, (vers) => {
                return {
                    text: versionToFull[vers],
                    link: `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.toUpperCase()}`,
                    onClick: (e) => {
                        history.push(
                            `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.toUpperCase()}`,
                        );
                    },
                };
            })}
        />
    );
}

export default withRouter(BillVersionsBreadcrumb);
