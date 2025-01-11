import { useContext } from "react";
import {
    Section,
    SectionCard,
    NonIdealState,
    NonIdealStateIconSize,
} from "@blueprintjs/core";

import { BillTable } from "components";
import { LoginContext } from "context";

function AuthedHome() {
    const { favoriteBills, favoriteSponsors } = useContext(LoginContext);

    return (
        <SectionCard>
            <div className="sidebar">
                <SectionCard>
                    <div className="section-detail">
                        <span className="section-detail-label">
                            Current Congress:
                        </span>
                        <span className="section-detail-value">
                            119th Session
                        </span>
                    </div>

                    <div className="section-detail">
                        <span className="section-detail-label">
                            Bills Introduced:
                        </span>
                        <span className="section-detail-value">243 Bills</span>
                    </div>
                </SectionCard>
            </div>

            <div className="content">
                <Section
                    title="Followed Legislation"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                >
                    {favoriteBills?.length > 0 ? (
                        <BillTable bills={favoriteBills} />
                    ) : (
                        <NonIdealState
                            icon="inbox"
                            iconSize={NonIdealStateIconSize.STANDARD}
                            title="No legislation results for this week"
                            description={
                                <>
                                    Try adding more legislation to favorites,
                                    <br />
                                    or check back later.
                                </>
                            }
                            layout="vertical"
                        />
                    )}
                </Section>

                <Section
                    title="Followed Sponsors"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                >
                    {favoriteSponsors?.length > 0 ? (
                        <BillTable bills={favoriteSponsors} />
                    ) : (
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
                    )}
                </Section>
            </div>
        </SectionCard>
    );
}

export default AuthedHome;
