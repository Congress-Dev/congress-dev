import { SectionCard, Section } from "@blueprintjs/core";

function LearnDifferences({ navigation }) {
    return (
        <Section
            className="page"
            title="Key Differences Between the House and Senate"
            subtitle="Comparing the Two Chambers: Roles, Structure, and Procedures"
        >
            {navigation}
            <SectionCard className="learn-content">
                <p>
                    The United States Congress is a bicameral legislature,
                    meaning it has two chambers: the House of Representatives
                    and the Senate. While both chambers play vital roles in the
                    legislative process, they have distinct structures, powers,
                    and functions that reflect the framers’ intent for a system
                    of checks and balances. Here’s a comparative overview of the
                    two chambers, highlighting their key differences:
                </p>

                <h2>1. Size and Representation</h2>
                <p>
                    The most obvious difference between the House and Senate is
                    their size and the way they represent the people.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> The House is larger,
                        with 435 members. Representatives are apportioned based
                        on population, meaning states with larger populations
                        have more representatives. Every 10 years, the
                        population data from the U.S. Census is used to
                        reallocate seats among the states. This system ensures
                        that the House represents the people more directly and
                        proportionally to their population.
                    </li>
                    <li>
                        <b>Senate:</b> The Senate is smaller, with 100 members,
                        two from each state regardless of population. This gives
                        equal representation to every state, ensuring that
                        smaller states have the same influence as larger ones.
                        Senators represent entire states rather than specific
                        districts.
                    </li>
                </ul>

                <h2>2. Term Lengths and Elections</h2>
                <p>
                    Another significant difference lies in how long members
                    serve and how they are elected.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> Members of the House
                        serve two-year terms and are elected by voters in their
                        districts. Because their terms are short,
                        Representatives are more accountable to their
                        constituents and must run for re-election frequently. As
                        a result, they tend to be more responsive to the
                        changing political climate and public opinion.
                    </li>
                    <li>
                        <b>Senate:</b> Senators serve six-year terms, with
                        elections held for about one-third of the Senate every
                        two years. This longer term allows Senators to focus on
                        long-term issues and policy decisions. The staggered
                        elections ensure that the Senate remains a more stable
                        body, with not all members facing re-election at the
                        same time.
                    </li>
                </ul>

                <h2>3. Leadership and Organization</h2>
                <p>
                    The leadership structures of the two chambers also differ
                    significantly.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> The House is led by the
                        Speaker of the House, who is elected by the full House
                        and typically comes from the majority party. The Speaker
                        has significant influence over the legislative agenda,
                        committee assignments, and the flow of debates. Other
                        key leaders include the Majority and Minority Leaders,
                        as well as Whips, who help manage party discipline and
                        rally votes.
                    </li>
                    <li>
                        <b>Senate:</b> The Senate is technically led by the Vice
                        President of the United States, who serves as President
                        of the Senate, but the day-to-day operations are
                        overseen by the Majority Leader. The Majority Leader,
                        unlike the Speaker of the House, does not have as much
                        centralized control over the Senate’s agenda. The Senate
                        is often seen as more collegial, with individual
                        Senators having more autonomy to shape the legislative
                        process. Other leadership positions in the Senate
                        include the Minority Leader and the President Pro
                        Tempore, a largely ceremonial role held by the
                        longest-serving member of the majority party.
                    </li>
                </ul>

                <h2>4. Powers and Responsibilities</h2>
                <p>
                    While both chambers share many responsibilities, they each
                    have unique powers defined by the Constitution.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> The House has the
                        exclusive power to initiate revenue bills, such as tax
                        legislation and federal spending bills. This gives the
                        House significant influence over fiscal policy. The
                        House also plays a critical role in impeachment, as it
                        is the body that brings charges against a sitting
                        president or other officials.
                    </li>
                    <li>
                        <b>Senate:</b> The Senate has several distinct powers,
                        including the authority to approve or reject treaties
                        and confirm presidential appointments, such as judges,
                        cabinet members, and ambassadors. The Senate also serves
                        as the trial body for impeachment cases, determining
                        whether a federal official should be removed from office
                        following a House-impeached charge. In addition, the
                        Senate is often seen as the more deliberative body, with
                        debates on major issues often lasting longer due to its
                        smaller size and tradition of extended discussion.
                    </li>
                </ul>

                <h2>5. Debate and Voting Procedures</h2>
                <p>
                    Debate and voting procedures differ considerably between the
                    two chambers due to their size and structure.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> Due to its larger size,
                        the House has more structured and time-limited debates.
                        The Speaker has the power to set rules for debates, and
                        time limits are often placed on speeches. This helps
                        ensure that the House can move efficiently through a
                        large number of bills, but it also means less room for
                        extended discussion. Voting in the House is typically
                        done by voice vote or electronic voting.
                    </li>
                    <li>
                        <b>Senate:</b> The Senate is known for its tradition of
                        extended debate, which can sometimes result in
                        filibusters—prolonged speeches designed to delay or
                        block a vote. The filibuster can be ended by a cloture
                        motion, requiring a three-fifths majority vote. Senators
                        are often given more freedom to speak at length on
                        issues, and voting is usually done by voice vote, roll
                        call vote, or unanimous consent, depending on the
                        situation.
                    </li>
                </ul>

                <h2>6. Impeachment</h2>
                <p>
                    Both chambers have important roles in impeachment, but their
                    functions are distinct.
                </p>
                <ul>
                    <li>
                        <b>House of Representatives:</b> The House has the sole
                        authority to initiate impeachment proceedings. If the
                        House approves articles of impeachment by a simple
                        majority vote, the president or other official is
                        formally impeached and the case moves to the Senate.
                    </li>
                    <li>
                        <b>Senate:</b> The Senate acts as the jury in
                        impeachment trials. After the House impeaches a
                        president or official, the Senate holds a trial and
                        votes to determine whether to remove the individual from
                        office. A two-thirds majority is required to convict and
                        remove someone from office.
                    </li>
                </ul>
            </SectionCard>
        </Section>
    );
}

export default LearnDifferences;
