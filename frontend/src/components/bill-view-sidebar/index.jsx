import React, { useState } from "react";
import { Tabs, Tab, FormGroup, HTMLSelect, Switch } from "@blueprintjs/core";
import lodash from "lodash";

import {
    BillDiffSidebar,
    BillViewAnchorList,
    AppropriationTree,
} from "components";

function BillViewSidebar({
    congress,
    chamber,
    billVersion,
    setBillVers,
    billNumber,
    billVers,
    bill,
    dateAnchors,
    bill2,
    scrollContentIdIntoView,
    actionParse,
    setActionParse,
}) {
    const [selectedTab, setSelectedTab] = useState("bill");

    return (
        <Tabs
            id="sidebar-tabs"
            selectedTabId={selectedTab}
            onChange={setSelectedTab}
        >
            <Tab
                id="bill"
                title="Bill"
                panel={
                    <>
                        <FormGroup
                            label="Version:"
                            labelFor="bill-version-select"
                        >
                            <HTMLSelect
                                id="bill-version-select"
                                value={(billVers || "").toUpperCase()}
                                onChange={(e) =>
                                    setBillVers(e.currentTarget.value)
                                }
                                className="bp3"
                                options={lodash.map(
                                    bill.legislation_versions,
                                    (
                                        { legislation_version, effective_date },
                                        ind,
                                    ) => {
                                        return {
                                            label: `${legislation_version} ${effective_date !== "None" ? ` - ${effective_date}` : ""}`,
                                            value: legislation_version,
                                        };
                                    },
                                )}
                            />
                        </FormGroup>

                        <FormGroup label="Display Options:">
                            <Switch label="Highlight dates" />
                            <Switch label="Highlight spending" />
                            <Switch label="Highlight tags" />
                            <Switch
                                label="Action parsing details"
                                checked={actionParse}
                                onChange={() => setActionParse(!actionParse)}
                            />
                        </FormGroup>
                    </>
                }
            />
            <Tab
                id="ud"
                title="USCode"
                panel={
                    <BillDiffSidebar
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVersion={billVers || billVersion}
                        bill={bill}
                    />
                }
            />
            <Tab
                id="datelist"
                title="Dates"
                panel={
                    <BillViewAnchorList
                        anchors={dateAnchors}
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVersion={billVersion}
                    />
                }
            />
            {bill2 &&
                bill2.appropriations &&
                bill2.appropriations.length > 0 && (
                    <Tab
                        id="dollarlist"
                        title="Dollars"
                        panel={
                            <AppropriationTree
                                appropriations={bill2.appropriations}
                                onNavigate={scrollContentIdIntoView}
                            />
                        }
                    />
                )}
        </Tabs>
    );
}

export default BillViewSidebar;
