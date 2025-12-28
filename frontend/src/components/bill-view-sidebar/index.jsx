import React, { useState, useContext } from "react";
import { Tabs, Tab, SectionCard } from "@blueprintjs/core";

import { BillContext } from "context";

import {
    BillDiffSidebar,
    BillTableOfContents,
    BillVersionsBreadcrumb,
    BillVotes,
    AppropriationTree,
    EffectiveDateActions,
    LegislatorChip,
    TalkToBill,
    BillActions,
} from "components";

function BillViewSidebar() {
    const [selectedTab, setSelectedTab] = useState("toc");

    const { billSummary, bill, bill2 } = useContext(BillContext);

    return (
        <>
            <SectionCard>
                <div className="section-detail">
                    <span className="section-detail-label">Introduced:</span>
                    <span className="section-detail-value">
                        {bill?.legislation_versions != null
                            ? bill.legislation_versions[0].effective_date
                            : ""}
                    </span>
                </div>

                <div className="section-detail">
                    <span className="section-detail-label">Sponsor:</span>
                    <span className="section-detail-value">
                        <LegislatorChip sponsor={bill2?.sponsor} />
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
                {billSummary != null && billSummary[0] != null ? (
                    <i>{billSummary[0].summary}</i>
                ) : (
                    <i>No summary for this bill.</i>
                )}
            </SectionCard>

            <Tabs
                id="bill-sidebar-tabs"
                selectedTabId={selectedTab}
                onChange={setSelectedTab}
            >
                <Tab
                    id="toc"
                    title="Contents"
                    panel={<BillTableOfContents />}
                />
                <Tab
                    id="uscode"
                    title="Diffs"
                    panel={<BillDiffSidebar />}
                />

                <Tab
                    id="dollarlist"
                    title="Spending"
                    panel={<AppropriationTree />}
                />

                <Tab
                    id="effective-dates"
                    title="Effective Dates"
                    panel={<EffectiveDateActions />}
                />

                {bill2?.votes?.length > 0 && (
                    <Tab
                        id="votes"
                        title="Votes"
                        panel={<BillVotes />}
                    />
                )}
                {bill2?.actions?.length > 0 && (
                    <Tab
                        id="actions"
                        title="Actions"
                        panel={<BillActions />}
                    />
                )}
            </Tabs>
        </>
    );
}

export default BillViewSidebar;
