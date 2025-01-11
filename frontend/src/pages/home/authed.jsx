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
                    <p>
                        Your personalized dashboard is ready! Here’s a quick
                        glance at what’s happening in Congress right now:
                    </p>
                    <ul>
                        <li>
                            📜 [X New Bills Introduced]: Stay updated with the
                            latest proposals.
                        </li>
                        <li>
                            🏛 [Y Votes This Week]: See which bills are
                            progressing.
                        </li>
                        <li>
                            ⭐ [Your Tracked Legislation]: Keep an eye on the
                            bills you care about.
                        </li>
                    </ul>

                    <b>What’s next?</b>
                    <ul>
                        <li>Explore your customized recommendations.</li>
                        <li>Review your tracked legislators or committees.</li>
                        <li>
                            Stay informed and engaged in the democratic process!
                        </li>
                    </ul>
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
                    title="Followed Sponsors"
                    subtitle="Last 7 Days"
                    icon="drag-handle-vertical"
                >
                    {favoriteSponsors?.length > 0 ? (
                        <BillTable bills={favoriteSponsors} />
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
            </div>
        </SectionCard>
    );
}

export default AuthedHome;
