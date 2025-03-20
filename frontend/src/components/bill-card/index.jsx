import React, { useContext } from "react";
import { withRouter, Link } from "react-router-dom";
import { Callout, Tag, SectionCard } from "@blueprintjs/core";

import { PreferenceEnum, PreferenceContext } from "context";
import { chamberLookup } from "common/lookups";
import { BillVersionsBreadcrumb, LegislatorChip } from "components";

const USDollar = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
});

function BillCard({ bill }) {
    const { preferences } = useContext(PreferenceContext);

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
                        <Tag minimal={true} round={true}>
                            {tag}
                        </Tag>
                        {"  "}
                    </>
                ))}
                <br />
            </>
        );
    }
    function renderPolicyArea() {
        if (bill.policy_areas == null || bill.policy_areas.length == 0) {
            return;
        }
        return (
            <>
                <span style={{ fontWeight: "bold" }}>Policy Areas:</span>
                {bill.policy_areas.map((policy_area) => (
                    <>
                        <Tag minimal={true} round={true} intent={"success"}>
                            {policy_area}
                        </Tag>
                        {"  "}
                    </>
                ))}
                {bill.subjects?.map((subject) => (
                    <>
                        <Tag minimal={true} round={true} intent={"primary"}>
                            {subject}
                        </Tag>
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
                            <b>Introduced:</b> {bill.effective_date}
                        </span>
                        <br />
                    </>
                ) : (
                    <></>
                )}
                {bill.sponsor != null ? (
                    <>
                        <b>Sponsor:</b>{" "}
                        <LegislatorChip sponsor={bill.sponsor} />
                    </>
                ) : (
                    ""
                )}
                {bill.legislation_versions != null &&
                bill.legislation_versions.length > 0 ? (
                    <>
                        <b>Versions:</b> <BillVersionsBreadcrumb bill={bill} />
                        <br />
                    </>
                ) : (
                    <></>
                )}

                {preferences[PreferenceEnum.SHOW_TAGS] && renderTags()}
                {preferences[PreferenceEnum.SHOW_TAGS] && renderPolicyArea()}

                {preferences[PreferenceEnum.SHOW_APPROPRIATIONS] &&
                bill.appropriations ? (
                    <>
                        <b>Appropriations:</b>{" "}
                        {USDollar.format(bill.appropriations)}{" "}
                    </>
                ) : null}
            </Callout>
        </SectionCard>
    );
}

export default withRouter(BillCard);
