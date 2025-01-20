import { useContext } from "react";
import { Section, HTMLTable, Tag } from "@blueprintjs/core";

import { BillContext } from "context";

function BillVotes(props) {
    const { bill2 } = useContext(BillContext);

    return (
        <>
            {bill2.votes?.map((vote) => {
                return (
                    <>
                        <Section
                            className="vote-result"
                            compact={true}
                            title={vote.question}
                            subtitle={vote.datetime}
                            icon={vote.passed ? "endorsed" : "error"}
                            collapsible={true}
                            collapseProps={{
                                defaultIsOpen: false,
                            }}
                        >
                            <HTMLTable
                                compact={true}
                                striped={true}
                                className="vote-data"
                            >
                                <thead>
                                    <th>Result</th>
                                    <th>
                                        <Tag intent="danger">R</Tag>
                                    </th>
                                    <th>
                                        <Tag intent="primary">D</Tag>
                                    </th>
                                    <th>
                                        <Tag intent="warning">I</Tag>
                                    </th>
                                    <th>Total</th>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>
                                            <b>Yay</b>
                                        </td>
                                        <td>{vote.republican.yay}</td>
                                        <td>{vote.democrat.yay}</td>
                                        <td>{vote.independent.yay}</td>
                                        <td>{vote.total.yay}</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <b>Nay</b>
                                        </td>
                                        <td>{vote.republican.nay}</td>
                                        <td>{vote.democrat.nay}</td>
                                        <td>{vote.independent.nay}</td>
                                        <td>{vote.total.nay}</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <b>Present</b>
                                        </td>
                                        <td>{vote.republican.present}</td>
                                        <td>{vote.democrat.present}</td>
                                        <td>{vote.independent.present}</td>
                                        <td>{vote.total.present}</td>
                                    </tr>
                                    <tr>
                                        <td>
                                            <b>Abstain</b>
                                        </td>
                                        <td>{vote.republican.abstain}</td>
                                        <td>{vote.democrat.abstain}</td>
                                        <td>{vote.independent.abstain}</td>
                                        <td>{vote.total.abstain}</td>
                                    </tr>
                                </tbody>
                            </HTMLTable>
                        </Section>
                        <br />
                    </>
                );
            })}
        </>
    );
}

export default BillVotes;
