import React, { useContext } from "react";
import lodash from "lodash";

import { AppropriationItem } from "components";
import { BillContext } from "context";

const AppropriationTree = () => {
    const { bill2, scrollContentIdIntoView } = useContext(BillContext);

    function createNestedAppropriationTree(appropriations) {
        // Put all of them into a hashmap by parentId
        // then create a tuple of (parentId, children)
        // for all the ones with no parentId
        // sort them by their appropriationId
        // for each of them, render their children in a list under them
        let appropMap = {};
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
                    onNavigate={scrollContentIdIntoView}
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
                                onNavigate={scrollContentIdIntoView}
                            />
                        ))}
                    </div>,
                );
            }
        });
        return <>{results.map((x) => x)}</>;
    }

    return bill2 != null &&
        bill2.appropriations != null &&
        bill2.appropriations.length > 0 ? (
        createNestedAppropriationTree(bill2.appropriations)
    ) : (
        <p>
            There have been no appropriations parsed in the contents of this
            bill.
        </p>
    );
};

export default AppropriationTree;
