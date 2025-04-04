import React, { useEffect, useState, useContext } from "react";

import { Section, SectionCard, Button } from "@blueprintjs/core";

import {
    getMemberInfo,
    getMemberSponsoredLegislation,
    userRemoveLegislator,
    userAddLegislator,
} from "common/api";
import { titleLookup } from "common/lookups";
import { LegislatorProfile } from "components";
import { LoginContext } from "context";

function MemberViewer(props) {
    const { bioguideId } = props.match.params;
    const [memberInfo, setMemberInfo] = useState({});
    const [sponsoredLegislation, setSponsoredLegislation] = useState([]);
    const { user, favoriteSponsors, setFavoriteSponsors } =
        useContext(LoginContext);

    useEffect(() => {
        // Grab the info from the rest API
        getMemberInfo(bioguideId).then(setMemberInfo);
        getMemberSponsoredLegislation(bioguideId).then((response) => {
            setSponsoredLegislation(response.legislationSponsorships);
        });
    }, [bioguideId]);

    function handleSponsorFavorite() {
        if (favoriteSponsors?.includes(bioguideId)) {
            userRemoveLegislator(bioguideId).then((response) => {
                if (response.legislator != null) {
                    setFavoriteSponsors(response.legislator);
                }
            });
        } else {
            userAddLegislator(bioguideId).then((response) => {
                if (response.legislator != null) {
                    setFavoriteSponsors(response.legislator);
                }
            });
        }
    }

    return (
        <Section
            interactive={false}
            className="page"
            title={`${titleLookup[memberInfo.job] + ' ' ?? ''}${memberInfo.firstName} ${memberInfo.lastName}`}
            subtitle={`${memberInfo.party} (${memberInfo.state})`}
            rightElement={
                <>
                    {user != null && (
                        <Button
                            icon="star"
                            {...{
                                ...(favoriteSponsors?.includes(bioguideId) && {
                                    intent: "primary",
                                }),
                            }}
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
