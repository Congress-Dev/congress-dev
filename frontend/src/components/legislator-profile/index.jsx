import React from "react";
import { Link } from "react-router-dom";
import { SectionCard, Button, Icon, Section } from "@blueprintjs/core";

import { BillCard, BillTable } from "components";

const LegislatorProfile = ({
    bioguideId,
    firstName,
    middleName,
    lastName,
    imageUrl = "",
    imageSource = "",
    profile = "",
    sponsoredLegislation = [],
    compact = true,
}) => {
    // I will make an element that links to the real profile page at https://bioguide.congress.gov/search/bio/${bioguideId}

    const renderSponsoredLegislation = () => {
        return (
            <>
                <h3>Sponsored Legislation:</h3>

                {sponsoredLegislation.map((sponsorship) => (
                    <BillCard bill={sponsorship} />
                ))}
            </>
        );
    };
    function capitalizeFirstLetter(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
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
                bioData.birth = sentence.replace("born in", "");
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

        if (bioData.birth) {
            const dateRegex =
                /\b((?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec))\s*(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})\b/;
            const dateMatch = bioData.birth.match(dateRegex);

            let birthPlace = bioData.birth;
            let birthDay = null;
            if (dateMatch != null && dateMatch[0] != null) {
                birthDay = dateMatch[0];
                birthPlace = birthPlace.replace(`, ${birthDay}`, "");
            }

            if (birthDay != null) {
                const birthDate = new Date(birthDay); // Parse the date string
                const today = new Date(); // Get today's date
                let age = today.getFullYear() - birthDate.getFullYear(); // Calculate year difference
                const monthDiff = today.getMonth() - birthDate.getMonth(); // Calculate month difference

                // Adjust age if the current month/day is before the birth month/day
                if (
                    monthDiff < 0 ||
                    (monthDiff === 0 && today.getDate() < birthDate.getDate())
                ) {
                    age--;
                }

                htmlContent += `<p><b>Age:</b> ${age} (${birthDay})`;
            }

            htmlContent += `<p><b>Birthplace:</b> ${birthPlace}</p>`;
        }

        if (bioData.education) {
            htmlContent += `<p><b>Education:</b></p><ul class="details">`;
            bioData.education.forEach((item) => {
                htmlContent += `<li>${capitalizeFirstLetter(item)}</li>`;
            });
            htmlContent += `</ul>`;
        }

        if (bioData.career) {
            htmlContent += `<p><b>Career:</b></p><ul class="details">`;
            bioData.career.forEach((item) => {
                htmlContent += `<li>${capitalizeFirstLetter(item)}</li>`;
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

    function renderBiopicture() {
        return (
            <>
                <div className="image">
                    {imageUrl != null && imageUrl != "" ? (
                        <img src={imageUrl} />
                    ) : (
                        <Icon icon="user" />
                    )}
                </div>
                <i
                    dangerouslySetInnerHTML={{
                        __html: imageSource,
                    }}
                />
                <br />
                <a
                    target="_blank"
                    href={`https://bioguide.congress.gov/search/bio/${bioguideId}`}
                >
                    <span>Profile on congress.gov</span>
                </a>
            </>
        );
    }

    function renderProfile() {
        return (
            <>
                {profile != null && profile != "" ? (
                    <>
                        <p
                            dangerouslySetInnerHTML={{
                                __html: parseBiography(profile),
                            }}
                        />
                    </>
                ) : (
                    <></>
                )}
            </>
        );
    }

    if (compact) {
        return (
            <div className="legislator-profile">
                <SectionCard>
                    <div className="center">{renderBiopicture()}</div>
                </SectionCard>
                <SectionCard>{renderProfile()}</SectionCard>
                <p>
                    <Link to={`/member/${bioguideId}`}>
                        <Button intent="primary">View Full Profile</Button>
                    </Link>
                </p>
            </div>
        );
    } else {
        return (
            <div class="legislator-profile">
                <div class="sidebar">
                    <Section title="Biography" icon="manual" compact={true}>
                        <SectionCard>
                            <div className="center">{renderBiopicture()}</div>
                        </SectionCard>
                        <SectionCard>{renderProfile()}</SectionCard>
                    </Section>
                </div>

                <div class="content">
                    <Section
                        title="Sponsored Legislation"
                        subtitle="All Records"
                        icon="drag-handle-vertical"
                    >
                        {sponsoredLegislation?.length > 0 && (
                            <BillTable bills={sponsoredLegislation} />
                        )}
                    </Section>
                </div>
            </div>
        );
    }
};

export default LegislatorProfile;
