import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { getMemberInfo, getMemberSponsoredLegislation } from "../../common/api.js";
import LegislatorProfile from "../../components/members/legislatorProfile.jsx";

function MemberViewer(props) {
  const { bioguideId } = props.match.params;
  const [memberInfo, setMemberInfo] = useState({});
  const [sponsoredLegislation, setSponsoredLegislation] = useState({});

  useEffect(() => {
    // Grab the info from the rest API
    getMemberInfo(bioguideId).then(setMemberInfo);
    getMemberSponsoredLegislation(bioguideId).then(setSponsoredLegislation);
  }, [bioguideId])
  return <span><LegislatorProfile {...memberInfo} sponsoredLegislation={sponsoredLegislation.legislation_sponsorships || []}></LegislatorProfile></span >
};

export default MemberViewer;