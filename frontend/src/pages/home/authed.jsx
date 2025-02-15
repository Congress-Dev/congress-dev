import { useContext, useState, useEffect } from "react";
import {
    Section,
    SectionCard,
    NonIdealState,
    NonIdealStateIconSize,
} from "@blueprintjs/core";
import { ResponsiveCalendar } from '@nivo/calendar'

import {
    userGetLegislationFeed,
    userGetLegislatorFeed,
    userGetStats,
    userGetFolders,
    statsGetCalendar,
} from "common/api";
import { BillTable, USCTrackingTabs } from "components";
import { LoginContext, ThemeContext } from "context";

function AuthedHome() {
    const { user } = useContext(LoginContext);
    const { nivoTheme } = useContext(ThemeContext);
    const [legislationFeed, setLegislationFeed] = useState([]);
    const [legislatorFeed, setLegislatorFeed] = useState([]);
    const [stats, setStats] = useState(null);
    const [calendar, setCalendar] = useState([])

    console.log(nivoTheme)

    useEffect(() => {
        if (user != null) {
            userGetLegislationFeed().then((response) => {
                setLegislationFeed(response.legislation);
            });

            userGetLegislatorFeed().then((response) => {
                setLegislatorFeed(response.legislation);
            });

            userGetStats().then((response) => {
                setStats(response);
            });
            userGetFolders().then(console.log);
        }

        statsGetCalendar().then((response) => {
            setCalendar(response.data)
        })
    }, [user]);

    return (
        <SectionCard>
            <div className="sidebar">
                <SectionCard>
                    <p>
                        Your personalized dashboard is ready! Here’s a quick
                        glance at what’s happening in Congress right now:
                    </p>
                    {stats != null && (
                        <ul>
                            <li>
                                {stats.legislation} bill
                                {stats.legislation != 1 ? "s" : ""} introduced
                                this year.
                            </li>
                            <li>
                                {stats.versions} bill version
                                {stats.versions != 1 ? "s" : ""} parsed.
                            </li>
                            <li>
                                {stats.legislators} member
                                {stats.legislators != 1 ? "s" : ""}{" "}
                                {stats.legislators != 1 ? "have" : "has"}{" "}
                                introduced bills.
                            </li>
                        </ul>
                    )}

                    <b>What’s next?</b>
                    <ul>
                        <li>Review your tracked legislators or sponsors.</li>
                        <li>
                            Stay informed and engaged in the democratic process!
                        </li>
                    </ul>
                </SectionCard>
            </div>

            <div className="content">
                <Section
                    title="Legislation Calendar"
                    subtitle="Activity over the year"
                    icon="drag-handle-vertical"
                    compact="true"
                    collapsible={true}
                >
                    <div style={{height: '200px'}}>
                        <ResponsiveCalendar
                            data={calendar}
                            from="2025-02-01"
                            to="2025-07-20"
                            emptyColor={nivoTheme.annotations.outline.outlineColor}
                            colors={[ '#BDADFF', '#9881F3', '#7961DB', '#634DBF' ]}
                            margin={{ top: 40, left: 40, right: 20, bottom: 20 }}
                            yearSpacing={40}
                            monthBorderColor={nivoTheme.annotations.outline.stroke}
                            dayBorderWidth={2}
                            dayBorderColor={nivoTheme.annotations.outline.stroke}
                            theme={nivoTheme}
                        />
                    </div>
                </Section>
                <Section
                    className="half"
                    title="Followed Legislation"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                    compact={true}
                    collapsible={true}
                >
                    {legislationFeed?.length > 0 ? (
                        <BillTable bills={legislationFeed} />
                    ) : (
                        <SectionCard>
                            <NonIdealState
                                icon="inbox"
                                iconSize={NonIdealStateIconSize.STANDARD}
                                title="No legislation results for this week"
                                description={
                                    <>
                                        Try adding more legislation to
                                        favorites,
                                        <br />
                                        or check back later.
                                    </>
                                }
                                layout="vertical"
                            />
                        </SectionCard>
                    )}
                </Section>

                <Section
                    className="half"
                    title="Followed Sponsors"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                    compact={true}
                    collapsible={true}
                >
                    {legislatorFeed?.length > 0 ? (
                        <BillTable bills={legislatorFeed} />
                    ) : (
                        <SectionCard>
                            <NonIdealState
                                icon="inbox"
                                iconSize={NonIdealStateIconSize.STANDARD}
                                title="No sponsor results for this week"
                                description={
                                    <>
                                        Try adding more sponsors to favorites,
                                        <br />
                                        or check back later.
                                    </>
                                }
                                layout="vertical"
                            />
                        </SectionCard>
                    )}
                </Section>

                <Section
                    title="USC Tracking"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                    compact={true}
                    collapsible={true}
                >
                    <SectionCard>
                        <USCTrackingTabs />
                    </SectionCard>
                </Section>
            </div>
        </SectionCard>
    );
}

export default AuthedHome;
