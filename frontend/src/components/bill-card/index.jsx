import React from "react";
import lodash from "lodash";
import { withRouter, Link } from "react-router-dom";
import { Callout, Breadcrumbs, Breadcrumb, Button } from "@blueprintjs/core";

import { chamberLookup, versionToFull } from "common/lookups";

function BillCard({ bill }) {
    function genTitle() {
        const { legislation_versions = [] } = bill;

        return (
            <>
                <Link
                    to={`/bill/${bill.congress}/${bill.chamber}/${bill.number}/${legislation_versions[legislation_versions.length - 1].legislation_version}`}
                >
                    {`${chamberLookup[bill.chamber]} ${bill.number}`}
                </Link>
            </>
        );
    }

    function getFirstEffectiveDate() {
        const { legislation_versions = [] } = bill;
        const dateStr = legislation_versions[0].effective_date;
        return `${dateStr}`;
    }

    function renderVersions() {
        const { legislation_versions = [] } = bill;
        const len = legislation_versions.length;
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
                        text: versionToFull[
                            vers.legislation_version.toLowerCase()
                        ],
                        link: `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.legislation_version}`,
                    };
                })}
            />
        );
    }

    return (
        <Callout className="bill-card">
            <Button
                className="congress-link"
                icon="share"
                onClick={() => {
                    window.open(
                        `https://congress.gov/bill/${bill.congress}-congress/${bill.chamber}-bill/${bill.number}`,
                        "_blank",
                    );
                }}
            />
            <h2 style={{ marginTop: "0px", marginBottom: "0px" }}>
                {genTitle()} - {bill.title}
            </h2>
            <span style={{ fontWeight: "bold" }}>Versions:</span>{" "}
            {renderVersions()}
            <br/>
            <span className="bill-card-introduced-date">
                <span style={{ fontWeight: "bold" }}>Introduced:</span>{" "}
                {getFirstEffectiveDate()}
            </span>
            <br />
            <span style={{ fontWeight: "bold" }}>Tags:</span> <br />
        </Callout>
    );
}

export default withRouter(BillCard);
