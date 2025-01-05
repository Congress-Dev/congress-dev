import React from "react";
import { withRouter, Link } from "react-router-dom";
import {
    Callout,
    Button,
    Tag,
    CompoundTag,
    SectionCard,
} from "@blueprintjs/core";

import { chamberLookup, partyLookup } from "common/lookups";
import { BillVersionsBreadcrumb, LegislatorChip } from "components";

const USDollar = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
});

function BillCard({ bill }) {
    function genTitle() {
        const { legislation_versions = [] } = bill;
        let version = "";
        if (legislation_versions.length > 0) {
            version = `/${legislation_versions[legislation_versions.length - 1]}`;
        }

        return (
            <>
                <Link
                    to={`/bill/${bill.congress}/${bill.chamber}/${bill.number}${version}`}
                >
                    {`${chamberLookup[bill.chamber]} ${bill.number}`}
                </Link>
            </>
        );
    }

    function renderTags() {
        if (bill.tags == null || bill.tags.length == 0) {
            return;
        }

        return (
            <>
                <span style={{ fontWeight: "bold" }}>Tags:</span>
                {bill.tags.map((tag) => (
                    <>
                        <Tag>{tag}</Tag>
                        {"  "}
                    </>
                ))}
                <br />
            </>
        );
    }

    return (
        <SectionCard padded={false} className="bill-card">
            <Callout>
                <h2 style={{ marginTop: "0px", marginBottom: "0px" }}>
                    {genTitle()} - {bill.title}
                </h2>

                {bill.effective_date != null ? (
                    <>
                        <span className="bill-card-introduced-date">
                            <span style={{ fontWeight: "bold" }}>
                                Introduced:
                            </span>{" "}
                            {bill.effective_date}
                        </span>
                        <br />
                    </>
                ) : (
                    <></>
                )}
                {bill.sponsor != null ? (
                    <>
                        <span style={{ fontWeight: "bold" }}>Sponsor:</span>{" "}
                        <LegislatorChip sponsor={bill.sponsor} />
                    </>
                ) : (
                    ""
                )}
                {bill.legislation_versions != null &&
                bill.legislation_versions.length > 0 ? (
                    <>
                        <span style={{ fontWeight: "bold" }}>Versions:</span>{" "}
                        <BillVersionsBreadcrumb bill={bill} />
                        <br />
                    </>
                ) : (
                    <></>
                )}

                {renderTags()}

                {bill.appropriations ? (
                    <>
                        <span style={{ fontWeight: "bold" }}>
                            Appropriations:
                        </span>{" "}
                        {USDollar.format(bill.appropriations)}{" "}
                    </>
                ) : null}
            </Callout>
        </SectionCard>
    );
}

export default withRouter(BillCard);
