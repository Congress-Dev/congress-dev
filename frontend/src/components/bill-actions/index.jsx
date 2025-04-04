import { useContext } from "react";
import { Section, HTMLTable, Tag } from "@blueprintjs/core";

import { BillContext } from "context";

function BillActions(props) {
    const { bill2 } = useContext(BillContext);
    // TODO: When we start tracking committees, add a link when a commitee action comes up
    return (
        <>
            {bill2.actions?.map((action) => {
                return (
                    <>
                        <Section
                            className="bill-action"
                            compact={true}
                            title={action.text}
                            subtitle={`${action.sourceName} - ${action.actionDate.split("T")[0]}`}
                        ></Section>
                        <br />
                    </>
                );
            })}
        </>
    );
}

export default BillActions;
