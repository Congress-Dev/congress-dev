import React, { useState, useContext } from "react";
import { CompoundTag, Drawer, DrawerSize } from "@blueprintjs/core";

import { ThemeContext } from "context/theme";
import { partyLookup } from "common/lookups";

function LegislatorChip({ bill }) {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { isDarkMode, setIsDarkMode } = useContext(ThemeContext);

    return bill.sponsor != null ? (
        <>
            <span style={{ fontWeight: "bold" }}>Sponsor:</span>{" "}
            <CompoundTag
                intent={
                    bill.sponsor.party == "Republican"
                        ? "danger"
                        : bill.sponsor.party == "Democrat"
                          ? "primary"
                          : "none"
                }
                leftContent={
                    partyLookup[bill.sponsor.party] != null
                        ? partyLookup[bill.sponsor.party]
                        : bill.sponsor.party
                }
                onClick={() => {
                    setDrawerOpen(!drawerOpen);
                }}
            >
                &nbsp;{bill.sponsor.lastName}, {bill.sponsor.firstName}&nbsp;
            </CompoundTag>
            <Drawer
                size={DrawerSize.SMALL}
                className={"legislator-profile " + (isDarkMode ? "bp5-dark" : "")}
                isOpen={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                isCloseButtonShown={true}
                title={`${bill.sponsor.firstName} ${bill.sponsor.lastName}`}
            >
                <div class="center">
                    <img src={bill.sponsor.imageUrl} alt="No Member Photo" />
                    <i dangerouslySetInnerHTML={{ __html: bill.sponsor.imageSource }} />
                </div>
                <p dangerouslySetInnerHTML={{ __html: bill.sponsor.profile }} />
            </Drawer>
            <br />
        </>
    ) : (
        <></>
    );
}

export default LegislatorChip;
