import React, { useContext, useState } from "react";
import { Tree } from "@blueprintjs/core";

import { BillContext } from "context";

function BillTableOfContents(props) {
    const [treeExpansion, setTreeExpansion] = useState({ 0: true });
    const { textTree, scrollContentIdIntoView } = useContext(BillContext);

    function onNodeClick(e) {
        scrollContentIdIntoView(e.id);
    }

    function onExpand(node) {
        setTreeExpansion({ ...treeExpansion, [node.id]: true });
    }

    function onCollapse(node) {
        setTreeExpansion({ ...treeExpansion, [node.id]: false });
    }

    function getHeadings() {
        if (textTree == null || textTree.children == null) {
            return [];
        }

        const headings = [];
        let idx = 0;

        for (const child of textTree?.children) {
            const children = [];

            if (child.heading === "Short title") {
                continue;
            }

            for (const subchild of child.children) {
                children.push({
                    key: subchild.legislation_content_id,
                    id: subchild.legislation_content_id,
                    label: `${subchild.section_display} ${subchild.heading}`,
                    depth: 2,
                });
            }

            headings.push({
                key: child.legislation_content_id,
                id: child.legislation_content_id,
                label: child.heading,
                depth: 1,
                childNodes: children.length > 0 ? children : null,
                isExpanded:
                    treeExpansion[child.legislation_content_id] === true,
            });

            idx++;
        }

        return headings;
    }

    return (
        <Tree
            contents={getHeadings()}
            onNodeExpand={onExpand}
            onNodeCollapse={onCollapse}
            onNodeClick={onNodeClick}
        />
    );
}

export default BillTableOfContents;
