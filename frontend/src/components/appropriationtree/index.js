import lodash from "lodash";
import { Callout, HTMLTable, Tag } from "@blueprintjs/core";

const AppropriationItem = ({ appropriation, onNavigate }) => {
    // Function to handle click events
    const handleClick = () => {
        // This function could navigate to the specific clause in the legislation
        // For example, by setting the window's location hash to an anchor tag or by using a router navigation method
        onNavigate(appropriation.legislationContentId);
    };

    return (
        <>
            <Callout>
                <h4 className="appropriation-title" onClick={handleClick}>
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
};

const AppropriationTree = ({ appropriations, onNavigate }) => {
    function createNestedAppropriationTree(appropriations) {
        // Put all of them into a hashmap by parentId
        // then create a tuple of (parentId, children)
        // for all the ones with no parentId
        // sort them by their appropriationId
        // for each of them, render their children in a list under them
        let appropMap = {};
        let appropTree = [];
        lodash.forEach(appropriations, (approp) => {
            if (approp.parentId in appropMap) {
                appropMap[approp.parentId].push(approp);
            } else {
                appropMap[approp.parentId] = [approp];
            }
        });
        let results = [];
        let rootApprops = appropMap[null];
        rootApprops = lodash.sortBy(rootApprops, (x) => x.appropriationId);
        lodash.forEach(rootApprops, (rootApprop) => {
            let children = appropMap[rootApprop.appropriationId];
            results.push(
                <AppropriationItem
                    key={rootApprop.parentId}
                    appropriation={rootApprop}
                    onNavigate={onNavigate}
                />,
            );
            if (children) {
                children = lodash.sortBy(children, (x) => x.appropriationId);
                results.push(
                    <div
                        className="nested-appropriation"
                        style={{ paddingLeft: "25px" }}
                    >
                        {children.map((child) => (
                            <AppropriationItem
                                key={child.parentId}
                                appropriation={child}
                                onNavigate={onNavigate}
                            />
                        ))}
                    </div>,
                );
            }
        });
        return <>{results.map((x) => x)}</>;
    }

    return createNestedAppropriationTree(appropriations);
};

export default AppropriationTree;
