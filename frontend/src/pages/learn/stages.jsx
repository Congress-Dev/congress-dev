import { SectionCard, Section } from "@blueprintjs/core";

function LearnStages({ navigation }) {
    return (
        <Section
            className="page"
            title="Understanding the Stages of a Bill in the House and Senate"
            subtitle="Key Stages in the House and Senate"
        >
            {navigation}
            <SectionCard className="learn-content">
                <p>
                    The journey of a bill from introduction to becoming law
                    involves several stages that take place in both the House of
                    Representatives and the Senate. While the general process is
                    similar in both chambers, there are key differences in how
                    the stages are carried out. This section breaks down each
                    stage in detail, providing an overview of how a bill
                    progresses through Congress and highlighting the differences
                    between the House and Senate at each stage.
                </p>

                <h2>1. Introduction of the Bill</h2>
                <p>
                    Every bill begins with its introduction, which occurs when a
                    member of either the House or Senate formally submits a
                    proposed piece of legislation. In the House, bills are
                    introduced by Representatives, while in the Senate, they are
                    introduced by Senators. The bill is then assigned a number
                    and referred to the relevant committee based on its subject
                    matter.
                </p>
                <p>
                    - <b>House of Representatives:</b> Bills are introduced
                    during the House's daily session, and the Speaker of the
                    House assigns the bill to the appropriate committee for
                    further review. - <b>Senate:</b> Similarly, bills are
                    introduced during the Senate's session, and the bill is
                    referred to a committee for review by the Senate leadership.
                </p>

                <h2>2. Committee Consideration</h2>
                <p>
                    Once a bill is introduced, it is assigned to a relevant
                    committee that specializes in the bill’s subject matter. The
                    committee conducts detailed reviews, holds hearings, and may
                    propose amendments. This is a critical stage in the process
                    because committees have the power to shape or even block a
                    bill.
                </p>
                <p>
                    - <b>House of Representatives:</b> The House has a large
                    number of standing committees, each focusing on a specific
                    policy area. Bills are typically assigned to one of these
                    committees based on their content. If the committee approves
                    the bill, it moves forward to the next stage. -{" "}
                    <b>Senate:</b>
                    Like the House, the Senate also has specialized committees.
                    However, Senate committees tend to be smaller, and the
                    review process is often more deliberative. Amendments to the
                    bill can be introduced and debated within the committee, and
                    the bill may also be subject to hearings with expert
                    testimony.
                </p>

                <h2>3. Debating the Bill</h2>
                <p>
                    Once a bill passes through the committee stage, it moves to
                    the floor of either the House or Senate for debate. This is
                    where the full chamber considers the bill, discusses its
                    merits and drawbacks, and decides whether to move forward
                    with it.
                </p>
                <p>
                    - <b>House of Representatives:</b> Debate in the House is
                    typically more structured and time-limited. The Speaker of
                    the House sets the rules for debate, including how much time
                    each side can speak. The House often uses a "rules
                    committee" to set the terms of debate, and members may not
                    have the opportunity to speak as freely or at length as in
                    the Senate. - <b>Senate:</b> Debate in the Senate is
                    generally less restricted, allowing Senators more time to
                    discuss the bill. This can lead to more extensive debate,
                    and in some cases, filibusters may be used to delay or block
                    a vote. The Senate’s tradition of extended debate means that
                    bills may face much longer deliberations before reaching a
                    final vote.
                </p>

                <h2>4. Voting on the Bill</h2>
                <p>
                    After the debate, the bill is put to a vote. In both the
                    House and Senate, the vote can either be by voice vote,
                    roll-call vote, or electronic vote, depending on the
                    chamber’s rules. If a bill passes in one chamber, it moves
                    to the other chamber for consideration. The bill must pass
                    both the House and Senate in identical form before being
                    sent to the President for approval.
                </p>
                <p>
                    - <b>House of Representatives:</b> Voting in the House is
                    typically done via electronic voting, where members cast
                    their votes using a computerized system. The results are
                    displayed on a board. In some cases, voice votes may be
                    used, where the Speaker determines whether the "ayes" or
                    "nays" have it, but this is less common for significant
                    legislation. - <b>Senate:</b> In the Senate, voting is often
                    done by roll-call vote, where each Senator’s vote is
                    recorded individually. The Senate also has a more flexible
                    voting system, allowing for more debate and amendments
                    before the final vote takes place.
                </p>

                <h2>
                    5. Differences Between the House and Senate in the Bill
                    Process
                </h2>
                <p>
                    While the process for handling a bill is largely similar in
                    both chambers, there are some important differences in how
                    these stages are carried out.
                </p>
                <ul>
                    <li>
                        <b>Committee Procedures:</b> The House typically has
                        more committees with greater specialization, leading to
                        more structured and rapid reviews. In contrast, Senate
                        committees tend to be smaller and more deliberative,
                        allowing for longer discussions and more thorough
                        consideration.
                    </li>
                    <li>
                        <b>Debate Rules:</b> Debate in the House is more
                        controlled, with strict time limits. In the Senate,
                        debate is more open, which can lead to longer
                        discussions and the possibility of filibusters, where
                        Senators speak at length to delay or block legislation.
                    </li>
                    <li>
                        <b>Voting:</b> The House uses electronic voting for most
                        votes, making the process faster and more efficient. The
                        Senate often uses roll-call votes, which can take longer
                        due to the smaller size of the chamber and the greater
                        time allowed for discussion.
                    </li>
                </ul>

                <h2>6. Final Approval and Sending to the President</h2>
                <p>
                    After a bill passes both the House and Senate, it is sent to
                    the President for approval. The President can either sign
                    the bill into law or veto it. If the President vetoes the
                    bill, it returns to Congress, where both chambers can
                    override the veto with a two-thirds majority vote. If the
                    President does not act on the bill within ten days while
                    Congress is in session, it automatically becomes law.
                </p>
                <p>
                    - <b>House of Representatives & Senate:</b> If both chambers
                    pass the bill in identical form, it is sent to the President
                    for final action. In cases where there are differences
                    between the versions of the bill passed in the House and
                    Senate, a conference committee may be formed to reconcile
                    the differences before sending the final version to the
                    President.
                </p>
            </SectionCard>
        </Section>
    );
}

export default LearnStages;
