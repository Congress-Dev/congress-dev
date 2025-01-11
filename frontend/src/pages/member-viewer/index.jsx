import React, { useEffect, useState, useContext } from "react";

import { Section, SectionCard, Button } from "@blueprintjs/core";

import {
    getMemberInfo,
    getMemberSponsoredLegislation,
    userRemoveLegislator,
    userAddLegislator,
} from "common/api";
import { LegislatorProfile } from "components";
import { LoginContext } from "context";

function MemberViewer(props) {
    const { bioguideId } = props.match.params;
    const [memberInfo, setMemberInfo] = useState({});
    const [sponsoredLegislation, setSponsoredLegislation] = useState([]);
    const { user, favoriteSponsorIds, setFavoriteSponsors } =
        useContext(LoginContext);

    useEffect(() => {
        // Grab the info from the rest API
        getMemberInfo(bioguideId).then(setMemberInfo);
        getMemberSponsoredLegislation(bioguideId).then((response) => {
            setSponsoredLegislation(response.legislationSponsorships);
        });
    }, [bioguideId]);

    console.log(favoriteSponsorIds);

    function handleSponsorFavorite() {
        if (favoriteSponsorIds?.includes(bioguideId)) {
            userRemoveLegislator(bioguideId).then((response) => {
                if (response.legislation != null) {
                    setFavoriteSponsors(response.legislation);
                }
            });
        } else {
            userAddLegislator(bioguideId).then((response) => {
                if (response.legislation != null) {
                    setFavoriteSponsors(response.legislation);
                }
            });
        }
    }

    return (
        <Section
            interactive={false}
            className="page"
            title={`Rep. ${memberInfo.firstName} ${memberInfo.lastName}`}
            subtitle={`${memberInfo.party} (${memberInfo.state})`}
            rightElement={
                <>
                    {user != null && (
                        <Button
                            icon="star"
                            intent={
                                favoriteSponsorIds?.includes(bioguideId)
                                    ? "primary"
                                    : ""
                            }
                            onClick={handleSponsorFavorite}
                        />
                    )}
                </>
            }
        >
            <SectionCard>
                <LegislatorProfile
                    {...memberInfo}
                    sponsoredLegislation={sponsoredLegislation}
                    compact={false}
                ></LegislatorProfile>
            </SectionCard>
        </Section>
    );
}

export default MemberViewer;
