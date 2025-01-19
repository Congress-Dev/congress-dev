import { SectionCard, Section } from "@blueprintjs/core";

function LearnVotes({ navigation }) {
    return (
        <Section
            className="page"
            title="Types of Votes in the House and Senate"
            subtitle="Explore the key vote types that drive decision-making in Congress"
        >
            {navigation}
            <SectionCard className="learn-content">
                <p>
                    Over time, the legislative process in both the House and
                    Senate has become increasingly complex, leading to the
                    development of various vote types. Early in the history of
                    Congress, the procedures for decision-making were relatively
                    straightforward, but as the nation's needs grew and the
                    legislative body expanded, more specific mechanisms were
                    required to manage debate, amendment, and approval of bills.
                    Different vote types were introduced to address unique
                    scenarios, such as filibusters in the Senate,
                    non-controversial bills in the House, or the need to
                    expedite certain decisions. Today, these various vote types
                    allow for greater flexibility and efficiency in handling the
                    wide range of issues Congress faces, ensuring that lawmakers
                    can navigate complex legislative challenges while
                    maintaining order and fairness in the process.
                </p>

                <h2>Common House Vote Types</h2>
                <ul>
                    <li>
                        <b>On Motion to Suspend the Rules and Pass:</b> Used to
                        quickly pass non-controversial bills, typically
                        requiring a two-thirds majority.
                    </li>
                    <li>
                        <b>On Motion to Recommit with Instructions:</b> A motion
                        to send a bill back to committee with specific
                        instructions for amendments or further review.
                    </li>
                    <li>
                        <b>On Agreeing to the Amendment:</b> A vote on whether
                        to accept or reject an amendment made to a bill during
                        its consideration.
                    </li>
                    <li>
                        <b>On Passage of the Bill:</b> A vote on whether to pass
                        the bill after all amendments and debates have been
                        completed.
                    </li>
                    <li>
                        <b>
                            On Motion to Suspend the Rules and Pass, as Amended:
                        </b>{" "}
                        Similar to the first, but this occurs after the bill has
                        been amended during the suspension of rules.
                    </li>
                    <li>
                        <b>On Motion to Table:</b> A motion to set aside a bill
                        or motion, effectively halting its consideration without
                        a direct vote.
                    </li>
                    <li>
                        <b>On Motion to Adjourn:</b> A motion to end the
                        legislative day and adjourn the House for the day.
                    </li>
                    <li>
                        <b>On Final Passage of a Resolution:</b> A vote on the
                        final version of a resolution, such as a concurrent
                        resolution.
                    </li>
                    <li>
                        <b>On Motion to Strike the Enacting Clause:</b> A motion
                        to remove the enacting clause of a bill, which would
                        effectively defeat the bill.
                    </li>
                    <li>
                        <b>On Motion to Postpone:</b> A motion to delay further
                        consideration of a bill or motion.
                    </li>
                </ul>

                <h2>Common Senate Vote Types</h2>
                <ul>
                    <li>
                        <b>On Motion to Proceed:</b> A vote to allow a debate or
                        action to begin on a bill or resolution. It requires a
                        simple majority to proceed.
                    </li>
                    <li>
                        <b>On Cloture:</b> A vote to end debate on a bill,
                        typically to overcome a filibuster. It requires a
                        three-fifths majority.
                    </li>
                    <li>
                        <b>On Confirmation of a Nominee:</b> A vote to confirm a
                        presidential appointment, such as a cabinet nominee or a
                        federal judge.
                    </li>
                    <li>
                        <b>On Passage of a Bill:</b> A vote to approve or reject
                        a bill after it has been debated and amended.
                    </li>
                    <li>
                        <b>On an Amendment:</b> A vote to approve or reject a
                        proposed amendment to a bill.
                    </li>
                    <li>
                        <b>On the Motion to Table:</b> A motion to set aside a
                        bill or amendment, effectively preventing it from moving
                        forward.
                    </li>
                    <li>
                        <b>On Reconsideration:</b> A vote to reconsider a
                        previous vote. This is often done if there is a desire
                        to revisit a decision.
                    </li>
                    <li>
                        <b>On Motion to Adjourn:</b> A motion to end the
                        legislative day and adjourn the Senate.
                    </li>
                    <li>
                        <b>On Motion to Suspend the Rules:</b> A motion to
                        suspend the Senate’s procedural rules for expedited
                        consideration of a bill or resolution.
                    </li>
                    <li>
                        <b>On a Conference Report:</b> A vote to accept or
                        reject the report from a conference committee,
                        reconciling differences between House and Senate
                        versions of a bill.
                    </li>
                </ul>
            </SectionCard>
        </Section>
    );
}

export default LearnVotes;
