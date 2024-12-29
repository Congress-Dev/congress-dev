import { Breadcrumbs, Breadcrumb } from "@blueprintjs/core";
import lodash from "lodash";
import { Link, withRouter } from "react-router-dom";

import { versionToFull } from "common/lookups";

function BillVersionsBreadcrumb({ bill }) {
    const { legislation_versions = [] } = bill;

    return (
        <Breadcrumbs
            className="bill-versions"
            breadcrumbRenderer={({ text, link, ...rest }) => (
                <Breadcrumb {...rest}>
                    <Link to={link}>{text}</Link>
                </Breadcrumb>
            )}
            items={lodash.map(legislation_versions, (vers, ind) => {
                return {
                    text: versionToFull[vers.legislation_version.toLowerCase()],
                    link: `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.legislation_version}`,
                };
            })}
        />
    );
}

export default withRouter(BillVersionsBreadcrumb);
