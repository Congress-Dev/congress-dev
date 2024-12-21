import React from "react";
import { Card, Elevation, H5, H6, Divider } from "@blueprintjs/core";
import SponsoredLegislation from "./sponsoredLegislation";

const LegislatorProfile = ({
    bioguideId,
    firstName,
    middleName,
    lastName,
    imageUrl,
    sponsoredLegislation = [],
}) => {
    // I will make an element that links to the real profile page at https://bioguide.congress.gov/search/bio/${bioguideId}

    const renderSponsoredLegislation = () => {
        return sponsoredLegislation.map((sponsorship) => (
            <SponsoredLegislation {...sponsorship} />
        ));
    };

    return (
        <Card interactive={false} elevation={Elevation.TWO}>
            <div style={{ textAlign: "center" }}>
                <img
                    src={imageUrl}
                    alt={`${firstName} profile`}
                    style={{
                        width: "100px",
                        height: "100px",
                        borderRadius: "50%",
                    }}
                />
                <H5>
                    {firstName} {lastName}
                </H5>
                <a
                    href={`https://bioguide.congress.gov/search/bio/${bioguideId}`}
                >
                    <span>Profile on congress.gov</span>
                </a>
            </div>
            <Divider />
            <p>More information about the legislator...</p>
            <div>{renderSponsoredLegislation()}</div>>
        </Card>
    );
};

export default LegislatorProfile;
