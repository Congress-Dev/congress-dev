import React from "react";
import { Section, SectionCard, Callout } from "@blueprintjs/core";

function AboutUs() {
    return (
        <Section
            className="page about-us"
            title="About Us"
            subtitle="Understanding Congress, One Bill at a Time"
        >
            <SectionCard>
                <p>
                    Welcome to <b>Congress.dev</b>, your trusted tool for
                    exploring and understanding federal legislation. In a world
                    where legislative processes can seem opaque and
                    overwhelming, our platform provides clarity by offering an
                    intuitive and powerful way to track, parse, and analyze
                    federal bills and resolutions in real time. Whether you're a
                    policy analyst, developer, journalist, or simply a curious
                    citizen, we empower you with the tools to stay informed and
                    engaged with the lawmaking process.
                </p>
                <p>
                    At its core, the platform bridges the gap between raw
                    legislative data and actionable insights. It collects and
                    organizes information from official government sources,
                    presenting it in an easily digestible and searchable format.
                    From bill summaries to voting records, sponsor details, and
                    legislative histories, we ensure you have the full context
                    you need at your fingertips. For developers, the robust API
                    enables seamless integration of legislative data into
                    projects, fostering innovation and deeper analysis.
                </p>
                <p>
                    Transparency and accessibility are at the heart of what we
                    do. By demystifying federal legislation and making it
                    available to everyone, we contribute to a more informed and
                    engaged public. Join us in exploring the policies that shape
                    our nation and discover how this resource can keep you
                    connected to the legislative process.
                </p>

                <Callout>
                    <h3 className="bp5-heading">Our Data Sources:</h3>
                    <p>
                        The information provided on this platform is sourced
                        exclusively from publicly available, open-source
                        government datasets, including but not limited to data
                        published by the Library of Congress, the Government
                        Publishing Office (GPO), and official Congressional
                        websites such as congress.gov. These sources supply data
                        on federal legislation, voting records, bill texts, and
                        other legislative materials.
                    </p>
                    <p>
                        This site operates as an independent platform that
                        organizes, parses, and presents this data for public
                        use. While we strive to maintain accuracy and up-to-date
                        information, no warranties are made regarding the
                        completeness, accuracy, or timeliness of the data. Users
                        are encouraged to verify details by cross-referencing
                        the information with official sources.
                    </p>
                    <p>
                        All legislative data presented here is made available
                        under applicable laws governing public domain content,
                        ensuring it can be freely accessed and utilized by
                        individuals and organizations. The platform does not
                        claim ownership of this data and complies fully with all
                        relevant usage terms established by the original data
                        providers.
                    </p>
                    <ul>
                        <li>
                            <a
                                href="https://www.govinfo.gov/bulkdata"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                https://www.govinfo.gov/bulkdata
                            </a>
                            &nbsp;(Bill Text/Statuses)
                        </li>
                        <li>
                            <a
                                href="https://uscode.house.gov/download/priorreleasepoints.htm"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                https://uscode.house.gov/download/priorreleasepoints.htm
                            </a>
                            &nbsp;(USCode Text)
                        </li>
                    </ul>
                </Callout>

                <Callout>
                    <h3 className="bp5-heading">
                        Frequently Asked Questions (FAQs):
                    </h3>
                    <ol className="faq">
                        <li>
                            <b>How often is the data updated?</b>
                            <br />
                            We update our data regularly to ensure the most
                            current information is available. Most updates occur
                            in real time or within a few hours of changes being
                            published by official government sources.
                        </li>
                        <li>
                            <b>Who can use Congress.dev?</b>
                            <br />
                            Congress.dev is designed for everyone—from policy
                            analysts, journalists, and developers to everyday
                            citizens who want to stay informed about federal
                            legislation.
                        </li>
                        <li>
                            <b>Is there an API available for developers?</b>
                            <br />
                            Yes! Congress.dev provides a{" "}
                            <a
                                target="_blank"
                                href="https://api.congress.dev/openapi.yaml"
                            >
                                robust API
                            </a>{" "}
                            for developers to access legislative data
                            programmatically. You can integrate it into your
                            applications to create custom solutions or conduct
                            detailed analysis.
                        </li>
                        <li>
                            <b>Is Congress.dev free to use?</b>
                            <br />
                            Our core platform is free to use for general users.
                        </li>
                        <li>
                            <b>How can I track specific bills or topics?</b>
                            <br />
                            You can use our search and filtering tools to track
                            specific bills, topics, or keywords. Additionally,
                            users can sign up for alerts to receive updates on
                            legislation of interest.
                        </li>
                        <li>
                            <b>How accurate is the information provided?</b>
                            <br />
                            We rely on official government sources for all our
                            data, ensuring a high degree of accuracy. However,
                            we recommend cross-referencing with the original
                            sources for critical decisions.
                        </li>
                        <li>
                            <b>Can I contribute or report an issue?</b>
                            <br />
                            Absolutely! We value feedback from our users. If you
                            spot an issue or have suggestions, please{" "}
                            <a href="mailto:admin@congress.dev">
                                contact us
                            </a>{" "}
                            to reach out.
                        </li>
                        <li>
                            <b>Does Congress.dev provide legal advice?</b>
                            <br />
                            No, Congress.dev is an informational tool and does
                            not provide legal advice. For legal guidance,
                            consult a qualified attorney or legal expert.
                        </li>
                        <li>
                            <b>
                                How can I stay updated about new features or
                                updates?
                            </b>
                            <br />
                            You can follow us on{" "}
                            <a
                                target="_blank"
                                href="https://x.com/congress_dev"
                            >
                                X.com
                            </a>{" "}
                            for the latest news, updates, and feature releases.
                        </li>
                        <li>
                            <b>
                                Can I use the data for my own projects or
                                research?
                            </b>
                            <br />
                            Yes, all data on Congress.dev is sourced from public
                            domain datasets and can be freely used under
                            applicable laws. Be sure to review the terms of use
                            for the original data sources as well.
                        </li>
                    </ol>
                </Callout>
            </SectionCard>
        </Section>
    );
}

export default AboutUs;
