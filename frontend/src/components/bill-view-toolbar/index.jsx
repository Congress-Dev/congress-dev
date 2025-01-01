import React, { useContext } from "react";
import {
    Button,
    Popover,
    Menu,
    MenuItem,
    MenuDivider,
} from "@blueprintjs/core";

import { versionToFull } from "common/lookups";
import { BillContext } from "context";

function BillViewToolbar() {
    const billContext = useContext(BillContext);
    const menuItemsData = [
        { text: "Home", icon: "home", href: "/" },
        { text: "About", icon: "info-sign", href: "/about" },
        { text: "Contact", icon: "envelope", href: "/contact" },
    ];
    return (
        <>
            <Button icon="exclude-row" />
            <Button icon="bookmark" />
            <Popover
                content={
                    <Menu>
                        <MenuDivider title="Versions" />
                        {billContext.bill.legislation_versions?.map(
                            (v, ind) => (
                                <MenuItem
                                    key={ind}
                                    text={
                                        versionToFull[
                                            v.legislation_version.toLowerCase()
                                        ]
                                    }
                                    onClick={() =>
                                        billContext.setBillVers(
                                            v.legislation_version,
                                        )
                                    }
                                />
                            ),
                        )}

                        <MenuDivider title="Display Options" />
                        <MenuItem
                            text="Highlight dates"
                            icon={billContext.dateParse ? "small-tick" : "small-cross"}
                            onClick={() =>
                                billContext.setDateParse(!billContext.dateParse)
                            }
                        />
                        <MenuItem
                            text="Highlight dollars"
                            icon={billContext.dollarParse ? "small-tick" : "small-cross"}
                            onClick={() =>
                                billContext.setDollarParse(
                                    !billContext.dollarParse,
                                )
                            }
                        />
                        <MenuItem
                            text="Highlight actions"
                            icon={billContext.actionParse ? "small-tick" : "small-cross"}
                            onClick={() =>
                                billContext.setActionParse(
                                    !billContext.actionParse,
                                )
                            }
                        />
                    </Menu>
                }
                placement="bottom"
            >
                <Button icon="cog" />
            </Popover>
        </>
    );
}

export default BillViewToolbar;
