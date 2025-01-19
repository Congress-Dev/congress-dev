import { useHistory, Link } from "react-router-dom";
import {
    Breadcrumbs,
    Callout,
    Card,
    CardList,
    Section,
    SectionCard,
    Icon,
} from "@blueprintjs/core";

import LearnProcess from "./process";
import LearnDifferences from "./differences";
import LearnCommittees from "./committees";
import LearnStages from "./stages";
import LearnAmendments from "./amendments";
import LearnPresident from "./president";
import LearnVotes from "./votes";

function Learn(props) {
    const { section } = props.match.params;
    const history = useHistory();

    const navigation = (
        <SectionCard className="learn-nav">
            <Breadcrumbs
                breadcrumbRenderer={({ icon, text, link }) => (
                    <>
                        {icon != null && <Icon icon={icon} />}
                        {link != null ? <Link to={link}>{text}</Link> : text}
                    </>
                )}
                items={[
                    { icon: "home" },
                    { text: "Knowledge Base", link: "/learn" },
                    { text: "Amendments" },
                ]}
            />
        </SectionCard>
    );

    function getPageContent() {
        switch (section) {
            case "process":
                return <LearnProcess navigation={navigation} />;
            case "differences":
                return <LearnDifferences navigation={navigation} />;
            case "committees":
                return <LearnCommittees navigation={navigation} />;
            case "stages":
                return <LearnStages navigation={navigation} />;
            case "amendments":
                return <LearnAmendments navigation={navigation} />;
            case "president":
                return <LearnPresident navigation={navigation} />;
            case "votes":
                return <LearnVotes navigation={navigation} />;
        }
    }

    if (section != null) {
        return <>{getPageContent()}</>;
    }

    return (
        <Section
            className="page"
            title="Knowledge Base"
            subtitle="Your Guide to U.S. Lawmaking"
        >
            <SectionCard>
                <p>
                    Here, you can explore a variety of topics that will help you
                    understand how U.S. legislation works and how Congress
                    functions. Whether you're curious about the step-by-step
                    journey of a bill becoming a law, the differences between
                    the House and Senate, or the critical role of committees,
                    this section is designed to guide you through the
                    complexities of the legislative process. Dive into detailed
                    explanations, discover key insights, and empower yourself
                    with the knowledge to better engage with our democracy.
                    Start exploring today and gain a deeper understanding of how
                    laws are made and how you can make your voice heard!
                </p>
            </SectionCard>
            <Callout>
                <CardList className="learn-list" bordered={false}>
                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/process");
                        }}
                    >
                        The Legislative Process: How a Bill Becomes a Law
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/differences");
                        }}
                    >
                        Key Differences Between the House and Senate
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/committees");
                        }}
                    >
                        The Role of Committees in Congress
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/stages");
                        }}
                    >
                        Understanding the Stages of a Bill in the House and
                        Senate
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/votes");
                        }}
                    >
                        Types of Votes in the House and Senate
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/amendments");
                        }}
                    >
                        The Importance of Amendments and Reconciliation
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/president");
                        }}
                    >
                        The Role of the President and Veto Power
                        <Icon icon="chevron-right" />
                    </Card>
                </CardList>
            </Callout>
        </Section>
    );
}

export default Learn;
