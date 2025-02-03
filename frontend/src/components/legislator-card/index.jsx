import React from "react";
import { withRouter, Link } from "react-router-dom";
import { Callout, Tag, SectionCard } from "@blueprintjs/core";

import { chamberLookup } from "common/lookups";
import { BillVersionsBreadcrumb, LegislatorChip } from "components";

const USDollar = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
});

function LegislatorCard({ legislator, bill, history }) {
    const navigateToLegislatorPage = (bioguideId) => {
      history.push(`/member/${bioguideId}`);
    }
    const getPartyLetter = (party) => {
        if (party === "Democrat") {
            return "D";
        } else if (party === "Republican") {
            return "R";
        } else {
            return "I";
        }
    };
    return (
        <SectionCard padded={false} className={`legislator-card ${legislator.party.toLowerCase()}`} onClick={() => navigateToLegislatorPage(legislator.bioguideId)}>
            <Callout>
                <h2 style={{ marginTop: "0px", marginBottom: "0px" }}>
                    ({getPartyLetter(legislator.party)}) {legislator.lastName}, {legislator.firstName} - {legislator.state}
                </h2>
                <img height={50} width={50} src={legislator.imageUrl} alt="Legislator" />

            </Callout>
        </SectionCard>
    );
}

export default withRouter(LegislatorCard);
