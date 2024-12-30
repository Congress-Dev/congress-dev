import React, { useState, useContext } from "react";
import { CompoundTag, Drawer, DrawerSize } from "@blueprintjs/core";

import { ThemeContext } from "context/theme";
import { partyLookup } from "common/lookups";
import { LegislatorProfile } from "..";

function LegislatorChip({ sponsor }) {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { isDarkMode, setIsDarkMode } = useContext(ThemeContext);

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
                className={(isDarkMode ? "bp5-dark" : "")}
                isOpen={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                isCloseButtonShown={true}
                title={`${sponsor.firstName} ${sponsor.lastName}`}
            >
                <LegislatorProfile {...sponsor} />
            </Drawer>
            <br />
        </>
    ) : (
        <></>
    );
}

export default LegislatorChip;
