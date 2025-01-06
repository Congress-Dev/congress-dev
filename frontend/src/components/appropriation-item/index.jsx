import { Callout, HTMLTable, Tag } from "@blueprintjs/core";

function AppropriationItem({ appropriation, onNavigate }) {
    return (
        <>
            <Callout>
                <h4
                    className="appropriation-title"
                    onClick={() =>
                        onNavigate(appropriation.legislationContentId)
                    }
                >
                    {appropriation.parentId ? "Sub " : ""}Appropriation #
                    {appropriation.appropriationId}{" "}
                    {appropriation.newSpending && (
                        <Tag intent="warning">New Spending</Tag>
                    )}
                </h4>
                <HTMLTable
                    compact={true}
                    striped={true}
                    className="appropriation-item"
                >
                    <tbody>
                        <tr>
                            <td>
                                <b>Purpose</b>
                            </td>
                            <td>{appropriation.briefPurpose}</td>
                        </tr>
                        <tr>
                            <td>
                                <b>Amount</b>
                            </td>
                            <td>${appropriation.amount.toLocaleString()}</td>
                        </tr>
                        <tr>
                            <td>
                                <b>Until Expended</b>
                            </td>
                            <td>
                                {appropriation.untilExpended ? "Yes" : "No"}
                            </td>
                        </tr>
                        {appropriation.fiscalYears.length > 0 && (
                            <tr>
                                <td>
                                    <b>Fiscal Years</b>
                                </td>
                                <td>{appropriation.fiscalYears.join(", ")}</td>
                            </tr>
                        )}
                        {appropriation.expirationYear && (
                            <tr>
                                <td>
                                    <b>Expires</b>
                                </td>
                                <td>{appropriation.expirationYear}</td>
                            </tr>
                        )}
                    </tbody>
                </HTMLTable>
            </Callout>
            <br />
        </>
    );
}

export default AppropriationItem;
