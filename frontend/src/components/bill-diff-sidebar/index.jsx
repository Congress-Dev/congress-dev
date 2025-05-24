import React, { useEffect, useState, useContext } from "react";
import lodash from "lodash";
import { withRouter } from "react-router-dom";
import { Tree, Drawer, Spinner } from "@blueprintjs/core";

import { ThemeContext, BillContext } from "context";
import {
    getBillVersionDiffForSection,
    getBillVersionDiffSummaryv2,
} from "common/api";
import { USCView } from "components";
import "./styles.css";

function BillDiffSidebar() {
    const [tree, setTree] = useState([]);
    const [treeExpansion, setTreeExpansion] = useState({ 0: true });
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [diffs, setDiffs] = useState({});
    const [diffLocation, setDiffLocation] = useState(null);
    const [results, setResults] = useState(false);
    const { isDarkMode } = useContext(ThemeContext);

    const { congress, chamber, billNumber, bill, billVersion, billVersionId } =
        useContext(BillContext);

    function navigateToSection(node) {
        if (node.diffLocation == null) {
            return;
        }

        setDrawerOpen(true);
        setDiffs(null);
        setDiffLocation(node.diffLocation);

        getBillVersionDiffForSection(
            congress,
            chamber,
            billNumber,
            billVersion,
            node.diffLocation.short_title,
            node.diffLocation.section_number,
        ).then((diffs) => {
            setDiffs(diffs);
        });
    }

    useEffect(() => {
        if (billVersionId) {
            getBillVersionDiffSummaryv2(
              billVersionId
            ).then((res) => {
                if (res == null || res.length == 0) {
                    setResults(false);
                    return;
                }

                setResults(true);
                let n = 0;
                // TODO: Fix sorting for the amendment titles
                const sorted = lodash.sortBy(res, (x) => x.shortTitle);
                const children = lodash.map(
                    sorted,
                    ({ sections, shortTitle, longTitle }, ind) => {
                        const titleSects = lodash.sortBy(
                            sections,
                            (x) => x.sectionNumber,
                        );
                        n += 1;
                        return {
                            id: n,
                            icon: "book",
                            isExpanded: treeExpansion[n] === true,
                            label: `${shortTitle} - ${longTitle}`,
                            childNodes: lodash.map(titleSects, (obj, ind2) => {
                                n += 1;
                                return {
                                    id: n,
                                    label: `${obj.display.replace(/SS/g, "§")} ${obj.heading}${obj.repealed === true ? " (Repealed)" : ""}`,
                                    className: `section-tree${obj.repealed === true ? " repealed-section" : ""}`,
                                    diffLocation: { ...obj, shortTitle },
                                };
                            }),
                        };
                    },
                );
                setTree([
                    {
                        id: 0,
                        hasCaret: true,
                        icon: "th-list",
                        isExpanded: treeExpansion[0] === true,
                        label: `USC`,
                        childNodes: children,
                        className: "link",
                    },
                ]);
            });
        }
    }, [billVersionId, treeExpansion]);

    function onExpand(node) {
        setTreeExpansion({ ...treeExpansion, [node.id]: true });
    }

    function onCollapse(node) {
        setTreeExpansion({ ...treeExpansion, [node.id]: false });
    }

    return results ? (
        <>
            <Tree
                contents={tree}
                onNodeExpand={onExpand}
                onNodeCollapse={onCollapse}
                onNodeClick={navigateToSection}
            />
            <Drawer
                className={isDarkMode ? "bp5-dark" : ""}
                isOpen={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                isCloseButtonShown={true}
                title={
                    diffLocation != null
                        ? `USC - ${diffLocation.shortTitle}. ${diffLocation.longTitle}`
                        : ""
                }
            >
                {diffs != null && diffLocation != null ? (
                    <USCView
                        release={bill.usc_release_id || "latest"}
                        section={diffLocation.sectionNumber}
                        title={diffLocation.shortTitle}
                        diffs={diffs}
                        interactive={false}
                    />
                ) : (
                    <Spinner className="loading-spinner" intent="primary" />
                )}
            </Drawer>
        </>
    ) : (
        <p>
            There have been no modifications to the United States Code in the
            contents of this bill.
        </p>
    );
}

export default withRouter(BillDiffSidebar);
