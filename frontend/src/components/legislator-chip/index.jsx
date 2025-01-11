import React, { useState, useContext } from "react";
import { CompoundTag, Drawer, DrawerSize } from "@blueprintjs/core";

import { ThemeContext } from "context/theme";
import { partyLookup, partyIntent } from "common/lookups";
import { LegislatorProfile } from "..";

function LegislatorChip({ sponsor }) {
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { isDarkMode } = useContext(ThemeContext);

    return sponsor != null ? (
        <>
            <CompoundTag
                intent={partyIntent[sponsor.party]}
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
                className={isDarkMode ? "bp5-dark" : ""}
                isOpen={drawerOpen}
                icon="id-number"
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
