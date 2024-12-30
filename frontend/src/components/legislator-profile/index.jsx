import React from "react";
import { Link } from "react-router-dom";
import { Divider, Icon } from "@blueprintjs/core";

import { BillCard } from "components";

const LegislatorProfile = ({
    bioguideId,
    firstName,
    middleName,
    lastName,
    imageUrl = "",
    imageSource = "",
    profile = "",
    sponsoredLegislation = [],
}) => {
    // I will make an element that links to the real profile page at https://bioguide.congress.gov/search/bio/${bioguideId}

    const renderSponsoredLegislation = () => {
        return <>
            <h3>Sponsored Legislation:</h3>

            {sponsoredLegislation.map((sponsorship) => (
                <BillCard bill={sponsorship} />
            ))}
        </>
    };

    function parseBiography(text) {
        const bioData = {};

        // Split the string into sentences using semicolons and trim whitespace
        const sentences = text
            .split(";")
            .map((sentence) => sentence.trim())
            .filter(Boolean);

        // Extract fields from sentences
        sentences.forEach((sentence) => {
            if (sentence.toLowerCase().includes("born")) {
                bioData.birth = sentence.replace("born", "Born");
            } else if (sentence.toLowerCase().includes("graduated")) {
                bioData.education = bioData.education || [];
                bioData.education.push(sentence);
            } else if (sentence.toLowerCase().includes("attended")) {
                bioData.education = bioData.education || [];
                bioData.education.push(sentence);
            } else if (sentence.toLowerCase().includes("staff")) {
                bioData.career = bioData.career || [];
                bioData.career.push(sentence);
            } else if (sentence.toLowerCase().includes("appointed")) {
                bioData.appointment = sentence;
            } else if (sentence.toLowerCase().includes("chairman")) {
                bioData.chairman = sentence;
            } else if (sentence.toLowerCase().includes("vice chairman")) {
                bioData.viceChairman = sentence;
            } else if (sentence.toLowerCase().includes("elected")) {
                bioData.elected = sentence;
            }
        });

        // Generate HTML content
        let htmlContent = "";
        htmlContent += `<p><b>${bioData.birth}</b></p>`;

        if (bioData.education) {
            htmlContent += `<p><b>Education:</b></p><ul class="details">`;
            bioData.education.forEach((item) => {
                htmlContent += `<li>${item}</li>`;
            });
            htmlContent += `</ul>`;
        }

        if (bioData.career) {
            htmlContent += `<p><b>Career:</b></p><ul class="details">`;
            bioData.career.forEach((item) => {
                htmlContent += `<li>${item}</li>`;
            });
            htmlContent += `</ul>`;
        }

        if (bioData.appointment) {
            htmlContent += `<p><b>Appointment:</b> ${bioData.appointment}</p>`;
        }

        if (bioData.chairman) {
            htmlContent += `<p><b>Chairman:</b> ${bioData.chairman}</p>`;
        }

        if (bioData.viceChairman) {
            htmlContent += `<p><b>Vice Chairman:</b> ${bioData.viceChairman}</p>`;
        }

        if (bioData.elected) {
            htmlContent += `<p><b>Political Career:</b> ${bioData.elected}</p>`;
        }

        return htmlContent;
    }

    return (
        <div className="legislator-profile">
            <div className="center">
                <div className="image">
                    {imageUrl != null && imageUrl != "" ?
                        <img src={imageUrl} /> :
                        <Icon icon="user" />}
                </div>
                <i
                    dangerouslySetInnerHTML={{
                        __html: imageSource,
                    }}
                />
                <br/>
                <a
                    href={`https://bioguide.congress.gov/search/bio/${bioguideId}`}
                >
                    <span>Profile on congress.gov</span>
                </a>
            </div>
            <Divider />
            {profile != null && profile != "" ? (
                <>
                    <h3>Biography:</h3>
                    <p
                        dangerouslySetInnerHTML={{
                            __html: parseBiography(profile),
                        }}
                    />
                    <Divider />
                </>
            ): <></>}
            {sponsoredLegislation.length == 0 ? (<p>
                <Link to={`/member/${bioguideId}`}>
                    More information about the legislator...
                </Link>
            </p>) : <>
                <div>{renderSponsoredLegislation()}</div>
            </>}
        </div>
    );
};

export default LegislatorProfile;
