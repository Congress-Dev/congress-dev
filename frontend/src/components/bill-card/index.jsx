import React from "react";
import { withRouter, Link } from "react-router-dom";
import { Callout, Button, Tag } from "@blueprintjs/core";

import { chamberLookup } from "common/lookups";
import { BillVersionsBreadcrumb } from "components";

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
            <BillVersionsBreadcrumb bill={bill} />
            <br />
            <span className="bill-card-introduced-date">
                <span style={{ fontWeight: "bold" }}>Introduced:</span>{" "}
                {bill.legislation_versions[0].effective_date}
            </span>
            <br />
            <span style={{ fontWeight: "bold" }}>Tags:</span>
            {/* {(bill.tags.forEach((tag) => {
                <Tag>{tag}</Tag>
            }))}<br /> */}
        </Callout>
    );
}

export default withRouter(BillCard);
