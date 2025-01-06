import { SectionCard, Section, Breadcrumbs } from "@blueprintjs/core";

function LearnProcess() {
    return (
        <Section
            className="page"
            title="The Legislative Process: How a Bill Becomes a Law"
            subtitle="Understanding the Path of Legislation"
        >
            <SectionCard className="learn-nav">
                <Breadcrumbs
                    items={[
                        { icon: "home" },
                        { text: "Knowledge Base", href: "/learn" },
                        { text: "Process" },
                    ]}
                />
            </SectionCard>
            <SectionCard className="learn-content">
                <p>
                    Understanding how a bill becomes a law is crucial to
                    navigating the legislative system. The process is long and
                    involves multiple stages in both the House of
                    Representatives and the Senate, with opportunities for
                    revision, debate, and approval at each step. The legislative
                    process may seem complex, but it ensures that bills are
                    thoroughly reviewed, debated, and refined before becoming
                    law. Each stage is designed to allow for scrutiny,
                    compromise, and input from both sides of the political
                    aisle. While the process is challenging, it is a vital part
                    of how laws are created and how the government responds to
                    the needs of the people.Here’s a detailed step-by-step guide
                    to help you understand how a bill moves from introduction to
                    law:
                </p>

                <h2>1. Introduction of the Bill</h2>
                <p>
                    Every law begins with an idea. A bill can be introduced in
                    either the House or the Senate by a member of Congress. Once
                    introduced, the bill is assigned a number and is officially
                    recognized as legislation. The member who introduces the
                    bill becomes its sponsor, and others may join in as
                    co-sponsors to show support.
                </p>

                <h2>2. Committee Review</h2>
                <p>
                    After introduction, the bill is sent to the relevant
                    committee based on its topic. Committees are small groups of
                    lawmakers who focus on specific policy areas, like finance,
                    education, or foreign relations. Committees play a critical
                    role in reviewing the bill in detail, holding hearings to
                    gather testimony, and making changes through amendments.
                    Many bills do not make it out of committee, and this is
                    where much of the decision-making happens.
                </p>

                <h2>3. Mark-Up and Amendment</h2>
                <p>
                    During committee review, the bill is carefully examined,
                    debated, and amended. This stage, called "mark-up," allows
                    committee members to propose changes to the bill. Amendments
                    can be small, like correcting a typo, or substantial,
                    altering the bill’s content. Once the committee members are
                    satisfied with the changes, the bill is voted on in
                    committee. If it passes, it moves forward.
                </p>

                <h2>4. Floor Debate and Voting</h2>
                <p>
                    After a bill clears committee, it heads to the floor of the
                    House or Senate, where all members can debate its merits and
                    suggest further amendments. This is a critical stage, as
                    lawmakers express their support or opposition to the bill.
                    The bill may be debated for days or even weeks, depending on
                    its complexity. Following the debate, members vote on the
                    bill. In the House, this is typically done by voice vote or
                    recorded vote. In the Senate, a simple majority vote is
                    required to move the bill forward.
                </p>

                <h2>5. The Other Chamber</h2>
                <p>
                    Once the bill passes in one chamber (either the House or the
                    Senate), it moves to the other chamber for consideration.
                    The process of committee review, debate, and voting is
                    repeated in the second chamber. The second chamber may pass
                    the bill as is, reject it, or make amendments. If the bill
                    is amended, it must go back to the originating chamber for
                    approval. If both chambers pass different versions of the
                    bill, they must work to reconcile the differences, often
                    through a conference committee.
                </p>

                <h2>6. Conference Committee</h2>
                <p>
                    When the House and Senate have passed differing versions of
                    a bill, a conference committee is formed. This committee
                    consists of members from both chambers who work out the
                    differences between the two versions. They agree on a single
                    version of the bill, which is then sent back to both the
                    House and Senate for final approval. If both chambers agree
                    on the changes, the bill is ready for the next step.
                </p>

                <h2>7. Presidential Action</h2>
                <p>
                    Once the bill has passed both the House and Senate, it is
                    sent to the president for approval. The president can sign
                    the bill into law, at which point it becomes an official
                    law. If the president vetoes the bill, it is sent back to
                    Congress. Congress can attempt to override the veto with a
                    two-thirds majority vote in both chambers. If the veto is
                    not overridden, the bill dies.
                </p>

                <h2>8. Becoming Law</h2>
                <p>
                    If the president signs the bill or if Congress overrides a
                    veto, the bill becomes law. It is then assigned a public law
                    number and is officially incorporated into the U.S. Code,
                    the system that organizes the laws of the United States.
                </p>
            </SectionCard>
        </Section>
    );
}

export default LearnProcess;
