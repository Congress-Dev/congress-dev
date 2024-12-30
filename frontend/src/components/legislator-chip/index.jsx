import React, { useState, useContext } from "react";
import { CompoundTag, Drawer, DrawerSize } from "@blueprintjs/core";

import { ThemeContext } from "context/theme";
import { partyLookup } from "common/lookups";

function LegislatorChip({ sponsor }) {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { isDarkMode, setIsDarkMode } = useContext(ThemeContext);

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

    return sponsor != null ? (
        <>
            <span style={{ fontWeight: "bold" }}>Sponsor:</span>{" "}
            <CompoundTag
                intent={
                    sponsor.party == "Republican"
                        ? "danger"
                        : sponsor.party == "Democrat"
                          ? "primary"
                          : "none"
                }
                leftContent={
                    partyLookup[sponsor.party] != null
                        ? partyLookup[sponsor.party]
                        : sponsor.party
                }
                onClick={() => {
                    setDrawerOpen(!drawerOpen);
                }}
            >
                &nbsp;{sponsor.lastName}, {sponsor.firstName}&nbsp;
            </CompoundTag>
            <Drawer
                size={DrawerSize.SMALL}
                className={
                    "legislator-profile " + (isDarkMode ? "bp5-dark" : "")
                }
                isOpen={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                isCloseButtonShown={true}
                title={`${sponsor.firstName} ${sponsor.lastName}`}
            >
                <div class="center">
                    <img src={sponsor.imageUrl} alt="No Member Photo" />
                    <i
                        dangerouslySetInnerHTML={{
                            __html: sponsor.imageSource,
                        }}
                    />
                </div>
                <p
                    dangerouslySetInnerHTML={{
                        __html: parseBiography(sponsor.profile),
                    }}
                />
            </Drawer>
            <br />
        </>
    ) : (
        <></>
    );
}

export default LegislatorChip;
