import React, { useContext } from "react";
import { useHistory } from "react-router-dom";
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
    const history = useHistory();

    function renderDateTree() {
        const yearMap = {};

        billContext.dateAnchors?.forEach((anchor) => {
            if (anchor.hash !== undefined) {
                const [date, year] = anchor.title.split(", ");
                if (yearMap[year] == null) {
                    yearMap[year] = [];
                }

                yearMap[year].push({ date: date, hash: anchor.hash });
            }
        });



        return (
            billContext.dateAnchors?.length > 0 ?
            <>
                {Object.keys(yearMap).map((key, ind) => (
                    <MenuItem key={ind} text={key}>
                        {yearMap[key].map((anchor, index) => (
                            <MenuItem
                                key={`${key}-${index}`}
                                text={`${anchor.date}, ${key}`}
                                onClick={() => {
                                    history.replace({ hash: anchor.hash });
                                    document
                                        .getElementById(anchor.hash)
                                        .scrollIntoView();
                                }}
                            />
                        ))}
                    </MenuItem>
                ))}
            </> : <MenuItem text={"No Dates Found"} disabled={true} />
        );
    }

    return (
        <>
            <Button icon="exclude-row" />

            <Popover
                content={
                    <Menu>
                        <MenuDivider title="Dates" />
                        {renderDateTree()}
                    </Menu>
                }
                placement="bottom"
            >
                <Button icon="bookmark" />
            </Popover>

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
                                    intent={billContext.billVers == v.legislation_version ? "primary" : ""}
                                />
                            ),
                        )}

                        <MenuDivider title="Display Options" />
                        <MenuItem
                            text="Highlight dates"
                            icon={
                                billContext.dateParse
                                    ? "small-tick"
                                    : "small-cross"
                            }
                            onClick={() =>
                                billContext.setDateParse(!billContext.dateParse)
                            }
                        />
                        <MenuItem
                            text="Highlight dollars"
                            icon={
                                billContext.dollarParse
                                    ? "small-tick"
                                    : "small-cross"
                            }
                            onClick={() =>
                                billContext.setDollarParse(
                                    !billContext.dollarParse,
                                )
                            }
                        />
                        <MenuItem
                            text="Highlight actions"
                            icon={
                                billContext.actionParse
                                    ? "small-tick"
                                    : "small-cross"
                            }
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
