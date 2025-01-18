import React, { useContext } from "react";
import { useHistory } from "react-router-dom";
import {
    Button,
    Popover,
    Menu,
    MenuItem,
    MenuDivider,
} from "@blueprintjs/core";

import { userAddLegislation, userRemoveLegislation } from "common/api";
import { versionToFull } from "common/lookups";
import {
    LoginContext,
    BillContext,
    PreferenceContext,
    PreferenceEnum,
} from "context";

function BillViewToolbar() {
    const { user, favoriteBills, setFavoriteBills } = useContext(LoginContext);
    const { preferences, setPreference } = useContext(PreferenceContext);
    const billContext = useContext(BillContext);
    const history = useHistory();

    function handleBillFavorite() {
        if (favoriteBills?.includes(billContext.bill.legislation_id)) {
            userRemoveLegislation(billContext.bill.legislation_id).then(
                (response) => {
                    if (response.legislation != null) {
                        setFavoriteBills(response.legislation);
                    }
                },
            );
        } else {
            userAddLegislation(billContext.bill.legislation_id).then(
                (response) => {
                    if (response.legislation != null) {
                        setFavoriteBills(response.legislation);
                    }
                },
            );
        }
    }

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

        return billContext.dateAnchors?.length > 0 ? (
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
            </>
        ) : (
            <MenuItem text={"No Dates Found"} disabled={true} />
        );
    }

    return (
        <>
            <Button
                className="congress-link"
                icon="share"
                onClick={() => {
                    window.open(
                        `https://congress.gov/bill/${billContext.bill.congress}-congress/${billContext.bill.chamber}-bill/${billContext.bill.number}`,
                        "_blank",
                    );
                }}
            />

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

            {user != null && (
                <Button
                    icon="star"
                    {...{
                        ...(favoriteBills?.includes(
                            billContext.bill.legislation_id,
                        ) && { intent: "primary" }),
                    }}
                    onClick={handleBillFavorite}
                />
            )}

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
                                    intent={
                                        billContext.billVers ==
                                        v.legislation_version
                                            ? "primary"
                                            : ""
                                    }
                                />
                            ),
                        )}

                        <MenuDivider title="Display Options" />
                        <MenuItem
                            text="Highlight dates"
                            icon={
                                preferences[PreferenceEnum.HIGHLIGHT_DATES]
                                    ? "small-tick"
                                    : "small-cross"
                            }
                            onClick={() =>
                                setPreference(
                                    PreferenceEnum.HIGHLIGHT_DATES,
                                    !preferences[
                                        PreferenceEnum.HIGHLIGHT_DATES
                                    ],
                                )
                            }
                        />
                        <MenuItem
                            text="Highlight dollars"
                            icon={
                                preferences[PreferenceEnum.HIGHLIGHT_DOLLARS]
                                    ? "small-tick"
                                    : "small-cross"
                            }
                            onClick={() =>
                                setPreference(
                                    PreferenceEnum.HIGHLIGHT_DOLLARS,
                                    !preferences[
                                        PreferenceEnum.HIGHLIGHT_DOLLARS
                                    ],
                                )
                            }
                        />
                        <MenuItem
                            text="Highlight actions"
                            icon={
                                preferences[PreferenceEnum.HIGHLIGHT_ACTIONS]
                                    ? "small-tick"
                                    : "small-cross"
                            }
                            onClick={() =>
                                setPreference(
                                    PreferenceEnum.HIGHLIGHT_ACTIONS,
                                    !preferences[
                                        PreferenceEnum.HIGHLIGHT_ACTIONS
                                    ],
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
