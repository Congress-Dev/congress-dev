import { useContext } from "react";
import { Link } from "react-router-dom";
import { SectionCard, Section, Button, Callout } from "@blueprintjs/core";

import { LoginContext } from "context";

function UnauthedHome() {
    const { handleLogin } = useContext(LoginContext);

    return (
        <div className="home-page-unauthed">
            <SectionCard>
                Welcome to <b>Congress.dev</b>, your trusted tool for exploring
                and understanding federal legislation. In a world where
                legislative processes can seem opaque and overwhelming, our
                platform provides clarity by offering an intuitive and powerful
                way to track, parse, and analyze federal bills and resolutions
                in real time. Whether you're a policy analyst, developer,
                journalist, or simply a curious citizen, we empower you with the
                tools to stay informed and engaged with the lawmaking process.
            </SectionCard>

            <SectionCard>
                <div className="sidebar">
                    <Section title="Key Features" icon="key">
                        <ul>
                            <li>
                                <b>Search Bills & Laws</b>
                                <br />
                                Easily find and explore federal legislation and
                                its impact on the U.S. Code.
                            </li>

                            <li>
                                <b>Track Your Interest</b>
                                <br />
                                Follow specific bills, lawmakers, or committees
                                to stay informed.
                            </li>

                            <li>
                                <b>Understand the Proces</b>
                                <br />
                                Learn how laws are made and track their progress
                                through Congress.
                            </li>
                        </ul>
                    </Section>
                </div>

                <Section
                    className="content"
                    title="Getting Started"
                    icon="drag-handle-vertical"
                >
                    <SectionCard>
                        <p>
                            At its core, the platform bridges the gap between
                            raw legislative data and actionable insights. It
                            collects and organizes information from official
                            government sources, presenting it in an easily
                            digestible and searchable format. From bill
                            summaries to voting records, sponsor details, and
                            legislative histories, we ensure you have the full
                            context you need at your fingertips. For developers,
                            the robust API enables seamless integration of
                            legislative data into projects, fostering innovation
                            and deeper analysis.
                        </p>
                        <p>
                            Transparency and accessibility are at the heart of
                            what we do. By demystifying federal legislation and
                            making it available to everyone, we contribute to a
                            more informed and engaged public. Join us in
                            exploring the policies that shape our nation and
                            discover how this resource can keep you connected to
                            the legislative process.
                        </p>
                        <Callout intent="primary" icon="clean">
                            <h3>Explore Legislation</h3>
                            <p>
                                Dive into the details of federal bills and
                                resolutions shaping the nation's future.
                            </p>
                            <Link to="/bills">
                                <Button intent="primary">Search Bills</Button>
                            </Link>
                        </Callout>

                        <Callout intent="primary" icon="series-configuration">
                            <h3>Sign Up to Customize Your Dashboard</h3>
                            <p>
                                Track the legislation and lawmakers that matter
                                to you.
                            </p>
                            <Button intent="primary" onClick={handleLogin}>
                                Login
                            </Button>
                        </Callout>
                    </SectionCard>
                </Section>
            </SectionCard>
        </div>
    );
}

export default UnauthedHome;
