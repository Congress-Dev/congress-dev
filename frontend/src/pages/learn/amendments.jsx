import { SectionCard, Section } from "@blueprintjs/core";

function LearnAmendments({ navigation }) {
    return (
        <Section
            className="page"
            title="The Importance of Amendments and Reconciliation"
            subtitle="How Changes and Compromises Shape a Bill"
        >
            {navigation}
            <SectionCard className="learn-content">
                <p>
                    Amendments are a crucial part of the legislative process,
                    allowing lawmakers to make changes to a bill before it
                    becomes law. Bills are rarely passed in their original form,
                    as they are typically amended during committee reviews,
                    floor debates, and negotiations between the House and
                    Senate. This section explains how bills are amended during
                    the legislative process and how the House and Senate
                    reconcile differences between their versions of a bill
                    before final passage.
                </p>

                <h2>1. Amendments in Committee</h2>
                <p>
                    The committee stage is where the bulk of a bill’s amendments
                    are made. Once a bill is introduced and assigned to a
                    committee, members of the committee review it in detail.
                    Committees can make significant changes to a bill, including
                    adding new provisions or removing sections entirely. These
                    amendments are debated and voted on within the committee,
                    and if approved, they become part of the bill that moves
                    forward to the full chamber for consideration.
                </p>
                <p>
                    - <b>House of Representatives:</b> In the House, committees
                    have the power to mark up bills, meaning they can amend the
                    text of the bill before it is reported out to the full
                    House. The House Rules Committee plays a central role in
                    determining how a bill will be debated, including how
                    amendments can be introduced during the debate. Amendments
                    made in committee are often more technical or focused on
                    specific issues, but they can also be more substantial,
                    altering the bill’s content or intent.
                </p>
                <p>
                    - <b>Senate:</b> In the Senate, the process of amending a
                    bill during committee review is similar to the House, but
                    Senate committees often allow for more debate on proposed
                    changes. Senators may offer amendments to the bill during
                    committee meetings, and the committee decides whether to
                    adopt those amendments before sending the bill to the full
                    Senate.
                </p>

                <h2>2. Amendments on the Floor</h2>
                <p>
                    After a bill is reported out of committee, it proceeds to
                    the floor of either the House or Senate for debate. During
                    floor debate, members of the chamber can propose additional
                    amendments to the bill. These amendments can be substantive,
                    changing the provisions of the bill, or technical,
                    correcting errors or clarifying language.
                </p>
                <p>
                    - <b>House of Representatives:</b> The House has stricter
                    rules for introducing amendments on the floor. The Rules
                    Committee sets the terms for debate, including how many
                    amendments can be offered and whether they will be debated
                    individually or as a group. In some cases, the House may
                    consider a "closed rule," which limits the number of
                    amendments that can be offered, or an "open rule," which
                    allows more flexibility in amending the bill during debate.
                </p>
                <p>
                    - <b>Senate:</b> In the Senate, the process for amending
                    bills on the floor is more flexible. Senators can propose
                    amendments directly during the debate, and those amendments
                    are typically debated individually. The Senate’s tradition
                    of extended debate means that amendments can be discussed in
                    detail, allowing Senators to offer substantial changes to
                    the bill’s text.
                </p>

                <h2>3. The Importance of Amendments in Shaping Legislation</h2>
                <p>
                    Amendments are vital in shaping the final version of a bill.
                    They allow lawmakers to address concerns, add provisions to
                    make the bill more effective, and negotiate compromises
                    between different factions. Through amendments, legislators
                    can refine the bill to meet the needs of their constituents
                    or to accommodate political negotiations. The amendment
                    process also ensures that bills are thoroughly reviewed and
                    debated before becoming law.
                </p>

                <h2>
                    4. Reconciliation: Resolving Differences Between the House
                    and Senate Versions
                </h2>
                <p>
                    After a bill passes one chamber, it must go through the same
                    process in the other chamber. However, the two chambers may
                    pass different versions of the same bill. These differences
                    must be reconciled before the bill can proceed to the
                    President for final approval.
                </p>
                <p>
                    - <b>Conference Committee:</b> When the House and Senate
                    pass different versions of a bill, a conference committee is
                    often formed to reconcile the differences. The committee is
                    made up of members from both the House and Senate, and its
                    job is to negotiate a compromise between the two versions of
                    the bill. The conference committee produces a final version
                    of the bill, known as the "conference report," which is then
                    sent back to both chambers for approval.
                </p>
                <p>
                    - <b>Consideration of the Conference Report:</b> Once the
                    conference committee agrees on a compromise, the conference
                    report is presented to both the House and Senate for a vote.
                    The members of each chamber vote on whether to accept or
                    reject the report. If both chambers approve the conference
                    report, the bill moves to the President for final approval.
                    If either chamber rejects the report, the bill may be sent
                    back to the conference committee for further negotiation or
                    die altogether.
                </p>

                <h2>5. The Role of Amendments in the Reconciliation Process</h2>
                <p>
                    Amendments play a critical role in the reconciliation
                    process between the House and Senate. As conference
                    committees work to resolve differences between the two
                    versions of a bill, they may propose additional amendments
                    to address concerns raised by both chambers. The final
                    version of the bill often reflects a series of compromises
                    that include amendments from both the House and Senate. This
                    ensures that the bill can pass through both chambers and be
                    sent to the President for approval.
                </p>

                <h2>6. Final Passage and Presidential Approval</h2>
                <p>
                    Once both the House and Senate agree on a final version of
                    the bill, it is sent to the President for approval. The
                    President can either sign the bill into law or veto it. If
                    the President vetoes the bill, it returns to Congress, where
                    both chambers can attempt to override the veto with a
                    two-thirds majority vote. If the bill is not vetoed, it
                    becomes law, and any amendments made during the legislative
                    process are now part of the final law.
                </p>
            </SectionCard>
        </Section>
    );
}

export default LearnAmendments;
