import React, { useEffect, useState } from "react";

import {
    getMemberInfo,
    getMemberSponsoredLegislation,
} from "common/api";
import { LegislatorProfile } from "components";

function MemberViewer(props) {
    const { bioguideId } = props.match.params;
    const [memberInfo, setMemberInfo] = useState({});
    const [sponsoredLegislation, setSponsoredLegislation] = useState({});

    useEffect(() => {
        // Grab the info from the rest API
        getMemberInfo(bioguideId).then(setMemberInfo);
        getMemberSponsoredLegislation(bioguideId).then(setSponsoredLegislation);
    }, [bioguideId]);

    return (
        <span>
            <LegislatorProfile
                {...memberInfo}
                sponsoredLegislation={
                    sponsoredLegislation.legislation_sponsorships || []
                }
            ></LegislatorProfile>
        </span>
    );
}

export default MemberViewer;
