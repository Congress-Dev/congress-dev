import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { getMemberInfo } from "../../common/api.js";
import LegislatorProfile from "../../components/members/legislatorProfile.jsx";

function MemberViewer(props) {
  const { bioguideId } = props.match.params;
  const [memberInfo, setMemberInfo] = useState({});
  useEffect(() => {
    // Grab the info from the rest API
    getMemberInfo(bioguideId).then(setMemberInfo);

  }, [bioguideId])
  return <span><LegislatorProfile {...memberInfo}></LegislatorProfile></span>
};

export default MemberViewer;