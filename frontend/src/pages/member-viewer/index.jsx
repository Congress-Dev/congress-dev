import React, { useEffect, useState } from "react";

import { Card, Elevation } from "@blueprintjs/core";

import { getMemberInfo, getMemberSponsoredLegislation } from "common/api";
import { LegislatorProfile } from "components";

function MemberViewer(props) {
    const { bioguideId } = props.match.params;
    const [memberInfo, setMemberInfo] = useState({});
    const [sponsoredLegislation, setSponsoredLegislation] = useState([]);

    useEffect(() => {
        // Grab the info from the rest API
        getMemberInfo(bioguideId).then(setMemberInfo);
        getMemberSponsoredLegislation(bioguideId).then((response) => {
            setSponsoredLegislation(response.legislationSponsorships);
        });
    }, [bioguideId]);

    return (
        <Card interactive={false} elevation={Elevation.TWO} className="page">
            <h1 style={{ textAlign: "center" }}>
                Rep. {memberInfo.firstName} {memberInfo.lastName} -{" "}
                {memberInfo.party} ({memberInfo.state})
            </h1>
            <LegislatorProfile
                {...memberInfo}
                sponsoredLegislation={sponsoredLegislation}
            ></LegislatorProfile>
        </Card>
    );
}

export default MemberViewer;
