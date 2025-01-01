import React, { useState, useContext } from "react";
import { Tabs, Tab, SectionCard } from "@blueprintjs/core";

import { BillContext } from "context";

import {
    BillDiffSidebar,
    BillVersionsBreadcrumb,
    AppropriationTree,
    LegislatorChip,
} from "components";

function BillViewSidebar(props) {
    const [selectedTab, setSelectedTab] = useState("uscode");

    const {
        congress,
        chamber,
        billNumber,
        billSummary,
        billVers,
        bill,
        dateAnchors,
        bill2,
        scrollContentIdIntoView,
        billVersion,
    } = useContext(BillContext);

    return (
        <>
            <SectionCard>
                <div className="section-detail">
                    <span className="section-detail-label">Introduced:</span>
                    <span className="section-detail-value">
                        {bill.legislation_versions != null
                            ? bill.legislation_versions[0].effective_date
                            : ""}
                    </span>
                </div>

                <div className="section-detail">
                    <span className="section-detail-label">Sponsor:</span>
                    <span className="section-detail-value">
                        <LegislatorChip sponsor={bill2.sponsor} />
                    </span>
                </div>

                <div className="section-detail">
                    <span className="section-detail-label">Versions:</span>
                    <span className="section-detail-value">
                        <BillVersionsBreadcrumb bill={bill} />
                    </span>
                </div>
            </SectionCard>

            <SectionCard>
                {billSummary != null && billSummary[0] != null ?
                    <i>{billSummary[0].summary}</i> :
                    <i>No summary for this bill.</i>
                }
            </SectionCard>

            <Tabs
                id="sidebar-tabs"
                selectedTabId={selectedTab}
                onChange={setSelectedTab}
            >
                <Tab
                    id="uscode"
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
        </>
    );
}

export default BillViewSidebar;
