import { useHistory } from "react-router-dom";
import {
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

function Learn(props) {
    const { section } = props.match.params;
    const history = useHistory();

    function getPageContent() {
        switch (section) {
            case "process":
                return <LearnProcess />;
            case "differences":
                return <LearnDifferences />;
            case "committees":
                return <LearnCommittees />;
            case "stages":
                return <LearnStages />;
            case "amendments":
                return <LearnAmendments />;
            case "president":
                return <LearnPresident />;
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
                        <b>The Legislative Process: How a Bill Becomes a Law</b>
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/differences");
                        }}
                    >
                        <b>Key Differences Between the House and Senate</b>
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/committees");
                        }}
                    >
                        <b>The Role of Committees in Congress</b>
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/stages");
                        }}
                    >
                        <b>
                            Understanding the Stages of a Bill in the House and
                            Senate
                        </b>
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/amendments");
                        }}
                    >
                        <b>The Importance of Amendments and Reconciliation</b>
                        <Icon icon="chevron-right" />
                    </Card>

                    <Card
                        interactive={true}
                        onClick={() => {
                            history.push("/learn/president");
                        }}
                    >
                        <b>The Role of the President and Veto Power</b>
                        <Icon icon="chevron-right" />
                    </Card>
                </CardList>
            </Callout>
        </Section>
    );
}

export default Learn;
