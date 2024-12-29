import React, { useEffect, useState, useContext } from "react";
import lodash from "lodash";
import { withRouter } from "react-router-dom";
import { Tree, Drawer, Spinner } from "@blueprintjs/core";

import { ThemeContext } from "context/theme";
import {
    getBillVersionDiffSummary,
    getBillVersionDiffForSection,
} from "common/api";
import { USCView } from "components";

function BillDiffSidebar({ congress, chamber, billNumber, billVersion, bill }) {
    const [tree, setTree] = useState([]);
    const [treeExpansion, setTreeExpansion] = useState({ 0: true });
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [diffs, setDiffs] = useState({});
    const [diffLocation, setDiffLocation] = useState(null);
    const [results, setResults] = useState(false);
    const { isDarkMode, setIsDarkMode } = useContext(ThemeContext);

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
        if (congress && chamber && billNumber && billVersion) {
            getBillVersionDiffSummary(
                congress,
                chamber,
                billNumber,
                billVersion,
            ).then((res) => {
                if (res == null || res.length == 0) {
                    setResults(false);
                    return;
                }

                setResults(true);
                let n = 0;
                // TODO: Fix sorting for the amendment titles
                const sorted = lodash.sortBy(res, (x) => x.short_title);
                const children = lodash.map(
                    sorted,
                    ({ sections, short_title, long_title }, ind) => {
                        const titleSects = lodash.sortBy(
                            sections,
                            (x) => x.section_number,
                        );
                        n += 1;
                        return {
                            id: n,
                            icon: "book",
                            isExpanded: treeExpansion[n] === true,
                            label: `${short_title} - ${long_title}`,
                            childNodes: lodash.map(titleSects, (obj, ind2) => {
                                n += 1;
                                return {
                                    id: n,
                                    icon: "wrench",
                                    label: `${obj.display.replace("SS", "§")} ${obj.heading}`,
                                    className: "section-tree",
                                    diffLocation: { ...obj, short_title },
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
    }, [congress, chamber, billNumber, billVersion, treeExpansion]);

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
                        ? `USC - ${diffLocation.short_title}. ${diffLocation.long_title}`
                        : ""
                }
            >
                {diffs != null && diffLocation != null ? (
                    <USCView
                        release={bill.usc_release_id || "latest"}
                        section={diffLocation.section_number}
                        title={diffLocation.short_title}
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
