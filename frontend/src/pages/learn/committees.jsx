import { SectionCard, Section, Divider } from "@blueprintjs/core";

function LearnCommittees() {
    return (
        <Section
            className="page learn-content"
            title="The Role of Committees in Congress"
            subtitle="Shaping, Revising, and Reviewing Bills"
        >
            <SectionCard className="learn-content">
                <p>
                    Committees play a crucial role in the legislative process,
                    as they are where much of the work of Congress is done. They
                    review bills, conduct hearings, and make recommendations
                    that shape the final version of the legislation that reaches
                    the floor for a vote. By focusing on specific areas of
                    policy, committees provide detailed scrutiny of proposed
                    laws, ensuring that bills are thoroughly examined before
                    they are passed by the full House or Senate.
                </p>

                <h2>1. Committee Structure</h2>
                <p>
                    Both the House and Senate have various committees that
                    specialize in specific policy areas. These committees are
                    divided into standing committees, subcommittees, and select
                    committees. Standing committees handle permanent, ongoing
                    legislative work, while subcommittees focus on narrower
                    aspects within the committee's larger mandate. Select
                    committees are formed for specific purposes, often to
                    investigate issues or handle temporary matters.
                </p>

                <h2>2. The Committee Process: Reviewing Bills</h2>
                <p>
                    Once a bill is introduced, it is assigned to the relevant
                    committee based on its subject matter. Committees are made
                    up of a group of lawmakers who have expertise or interest in
                    that area. The committee members review the bill in detail,
                    debating its merits and considering how it aligns with
                    existing laws and policies. Often, committee members will
                    seek input from experts, stakeholders, and the public to
                    ensure that the bill is well-crafted and addresses the issue
                    effectively.
                </p>

                <h2>3. Conducting Hearings and Gathering Testimony</h2>
                <p>
                    One of the most important functions of committees is
                    conducting hearings. These hearings are public meetings
                    where committee members hear testimony from witnesses,
                    including experts, government officials, advocacy groups,
                    and other interested parties. Hearings allow lawmakers to
                    gather information and hear different perspectives on a
                    bill. Witnesses may testify in person or submit written
                    statements. This process helps committees gather the
                    evidence they need to make informed decisions about the
                    bill.
                </p>

                <h2>4. Mark-Up and Amendments</h2>
                <p>
                    After reviewing a bill and holding hearings, the committee
                    begins the "mark-up" process. During mark-up, committee
                    members go through the bill line by line, suggesting changes
                    or amendments. Amendments can be small, like correcting
                    typos, or they can be more significant, altering the
                    substance of the bill. These amendments are debated and
                    voted on by the committee. If the bill passes through the
                    committee with changes, it moves on to the next stage in the
                    legislative process. If the committee does not approve the
                    bill or the amendments are too significant, the bill may be
                    blocked at this stage.
                </p>

                <h2>5. The Power to Amend or Block Legislation</h2>
                <p>
                    Committees hold considerable power in shaping legislation.
                    They have the authority to make significant changes to a
                    bill or even block it entirely. If a committee votes to
                    reject a bill, it may not make it out of the committee and
                    thus never proceed to the floor of the House or Senate. This
                    makes committees a powerful gatekeeper in the legislative
                    process. The decisions made at the committee level often
                    determine whether a bill will proceed to the next stage or
                    fail to advance.
                </p>

                <h2>6. Reporting the Bill to the Full Chamber</h2>
                <p>
                    If a committee approves a bill, it is "reported out" to the
                    full House or Senate. The bill is then placed on the
                    chamber’s legislative calendar for debate and consideration.
                    However, even after a bill leaves committee, the full
                    chamber may make further amendments or revisions. While
                    committees are instrumental in shaping a bill, the final
                    version can still change based on the decisions of the full
                    House or Senate during debate and voting.
                </p>

                <h2>7. The Importance of Committees in Legislation</h2>
                <p>
                    Committees are essential to the functioning of Congress.
                    They allow for focused, in-depth analysis of proposed
                    legislation, ensuring that bills are thoroughly vetted
                    before being presented to the full chamber. Committees also
                    provide a venue for lawmakers to engage with experts and
                    constituents, giving them a deeper understanding of the
                    issues at hand. Without committees, it would be impossible
                    for Congress to manage the vast number of bills introduced
                    each year, and the legislative process would be far less
                    efficient.
                </p>
            </SectionCard>
        </Section>
    );
}

export default LearnCommittees;
