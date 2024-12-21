// Renders the sidebar for the applicable location we are in.
import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { withRouter } from "react-router-dom";
import { Tree } from "@blueprintjs/core";

import {
    getUSCTitleList,
    getUSCLevelSections,
    getUSCSectionLineage,
} from "common/api";

function USCSidebar(props) {
    const [tree, setTree] = useState([]);
    const [treeExpansion, setTreeExpansion] = useState({ 0: true });
    const [internalTree, setInternalTree] = useState({});

    useEffect(() => {
        if (!props.title) {
            getUSCTitleList(props.release).then((res) => {
                let n = 0;
                let intUpdates = {};
                let childNodes = lodash.map(
                    res,
                    ({ short_title, long_title, usc_chapter_id }) => {
                        const nodeObj = {
                            id: `${usc_chapter_id}`,
                            icon: "book",
                            isExpanded:
                                treeExpansion[`${usc_chapter_id}`] === true,
                            label: `${short_title} - ${long_title}`,
                            short_title,
                            usc_chapter_id,
                            childNodes: [],
                        };
                        intUpdates[nodeObj.id] = [];
                        return nodeObj;
                    },
                );
                const rootNode = {
                    id: 0,
                    hasCaret: true,
                    icon: "th-list",
                    isExpanded: treeExpansion[0] === true,
                    label: `Hmmst`,
                    childNodes,
                    className: "link",
                };
                setTree([rootNode]);
                setInternalTree({
                    ...internalTree,
                    ...intUpdates,
                    [0]: childNodes,
                });
            });
        } else {
            // TODO: When a user lands on the section url, we need to drill down and expand for them
            // getUSCSectionList(props.release, props.title).then(setSectionList);
            getUSCTitleList(props.release).then((res) => {
                let n = 0;
                let intUpdates = {};
                let childNodes = lodash.map(
                    res,
                    ({ short_title, long_title, usc_chapter_id }) => {
                        // if(short_title == props.title) {
                        //   setTreeExpansion({...treeExpansion, [usc_chapter_id]: true});
                        // }
                        const nodeObj = {
                            id: `${usc_chapter_id}`,
                            icon: "book",
                            isExpanded:
                                short_title === props.title ||
                                treeExpansion[`${usc_chapter_id}`] === true,
                            label: `${short_title} - ${long_title}`,
                            short_title,
                            usc_chapter_id,
                            childNodes: [],
                        };
                        intUpdates[nodeObj.id] = [];
                        return nodeObj;
                    },
                );
                const rootNode = {
                    id: 0,
                    hasCaret: true,
                    icon: "th-list",
                    isExpanded: treeExpansion[0] === true,
                    label: `Hmmst`,
                    childNodes,
                    className: "link",
                };
                setTree([rootNode]);
                setInternalTree({
                    ...internalTree,
                    ...intUpdates,
                    [0]: rootNode.childNodes,
                });
                getUSCSectionLineage(
                    props.release,
                    props.title,
                    props.section,
                ).then((res) => {
                    const innerIntUpdates = {};
                    const expansionUpd = {};
                    let chapId = null;
                    let firstNode = [];
                    lodash.forEach(
                        res,
                        ({
                            parent_id,
                            number,
                            heading,
                            section_display,
                            usc_section_id,
                            content_type,
                            usc_chapter_id,
                        }) => {
                            if (!usc_chapter_id) {
                                return;
                            }
                            const nodeObj = {
                                id: `${usc_chapter_id}.${usc_section_id}`,
                                hasCaret: content_type !== "section",
                                icon:
                                    content_type !== "section" ? "book" : "dot",
                                label: `${section_display} ${heading}`,
                                className: "section-tree",
                                short_title: props.title,
                                usc_section_id,
                                number,
                                childNodes: [],
                            };
                            if (content_type === "chapter") {
                                const existingChildren =
                                    internalTree[`${usc_chapter_id}`] || [];
                                innerIntUpdates[`${usc_chapter_id}`] =
                                    lodash.uniqBy(
                                        [...existingChildren, nodeObj],
                                        "id",
                                    );
                                expansionUpd[`${usc_chapter_id}`] = true;
                            } else {
                                const existingChildren =
                                    internalTree[
                                        `${usc_chapter_id}.${parent_id}`
                                    ] || [];
                                innerIntUpdates[
                                    `${usc_chapter_id}.${parent_id}`
                                ] = lodash.uniqBy(
                                    [...existingChildren, nodeObj],
                                    "id",
                                );
                                expansionUpd[`${usc_chapter_id}.${parent_id}`] =
                                    true;
                            }
                            if (!chapId) {
                                chapId = `${usc_chapter_id}`;
                                firstNode = [nodeObj];
                            }
                        },
                    );
                    intUpdates[chapId] = firstNode;
                    setInternalTree({
                        ...internalTree,
                        ...intUpdates,
                        ...innerIntUpdates,
                        [0]: rootNode.childNodes,
                    });
                    setTreeExpansion({ ...treeExpansion, ...expansionUpd });
                });
            });
        }
    }, [props.section]);

    useEffect(() => {
        const newTree = lodash.map(tree, drillExpansion);
        setTree(newTree);
    }, [treeExpansion, internalTree]);

    function drillExpansion(node) {
        let childNodes = [];
        if (treeExpansion[node.id] === true) {
            childNodes = lodash.map(internalTree[node.id], drillExpansion);
        }
        return {
            ...node,
            isExpanded: treeExpansion[node.id] === true,
            childNodes: lodash.uniqBy(childNodes, "id"),
        };
    }

    function navigate(url) {
        props.history.push(url);
    }

    function navigateToSection(node) {
        if (node.number) {
            navigate(
                `/uscode/${props.release}/${node.short_title}/${node.number}`,
            );
            // props.history.push(
            //   `/bill/${congress}/${chamber}/${billNumber}/${billVersion}/diffs/${short_title}/${section_number}`
            // );
        } else if (node.id === 0) {
            // props.history.push(`/bill/${congress}/${chamber}/${billNumber}/${billVersion}`);
        }
    }

    function onExpand(node) {
        if (node.childNodes.length === 0) {
            getUSCLevelSections(
                props.release,
                node.short_title,
                node.usc_section_id,
            ).then((res) => {
                const intUpdates = {};
                const childNodes = lodash.map(
                    res,
                    ({
                        number,
                        heading,
                        section_display,
                        usc_section_id,
                        content_type,
                        usc_chapter_id,
                    }) => {
                        const nodeObj = {
                            id: `${usc_chapter_id}.${usc_section_id}`,
                            hasCaret: content_type !== "section",
                            icon: content_type !== "section" ? "book" : "dot",
                            label: `${section_display} ${heading}`,
                            className: "section-tree",
                            short_title: node.short_title,
                            usc_section_id,
                            number,
                            childNodes: [],
                        };
                        intUpdates[nodeObj.id] = [];
                        return nodeObj;
                    },
                );
                intUpdates[node.id] = childNodes;
                setInternalTree({ ...internalTree, ...intUpdates });
            });
        }
        setTreeExpansion({ ...treeExpansion, [node.id]: true });
    }

    function onCollapse(node) {
        setTreeExpansion({ ...treeExpansion, [node.id]: false });
    }

    return (
        <Tree
            contents={tree}
            onNodeExpand={onExpand}
            onNodeCollapse={onCollapse}
            onNodeClick={navigateToSection}
        />
    );
}

export default withRouter(USCSidebar);
