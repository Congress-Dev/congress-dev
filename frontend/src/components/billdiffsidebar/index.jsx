import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { withRouter } from "react-router-dom";

import { Tree } from "@blueprintjs/core";

import { getBillVersionDiffSummary, capFirstLetter } from "../../common/api.js";
import { chamberLookup } from "../../common/lookups.js";

function BillDiffSidebar(props) {
  const [tree, setTree] = useState([]);
  const [treeExpansion, setTreeExpansion] = useState({ 0: true });
  const { congress, chamber, billNumber, billVersion } = props;

  function navigateToSection(node) {
    if (node.diffLocation) {
      const { short_title, section_number } = node.diffLocation;
      props.history.push(
        `/bill/${congress}/${chamber}/${billNumber}/${billVersion}/diffs/${short_title}/${section_number}`
      );
    } else if (node.id === 0) {
      props.history.push(`/bill/${congress}/${chamber}/${billNumber}/${billVersion}`);
    }
  }
  useEffect(() => {
    if (congress && chamber && billNumber && billVersion) {
      getBillVersionDiffSummary(congress, chamber, billNumber, billVersion).then(
        res => {
          let n = 0;
          // TODO: Fix sorting for the amendment titles
          const sorted = lodash.sortBy(res, x => x.short_title);
          const children = lodash.map(
            sorted,
            ({ sections, short_title, long_title }, ind) => {
              const titleSects = lodash.sortBy(sections, x => x.section_number);
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
                    label: `${obj.display} ${obj.heading}`,
                    className: "section-tree",
                    diffLocation: { ...obj, short_title },
                  };
                }),
              };
            }
          );
          setTree([
            {
              id: 0,
              hasCaret: true,
              icon: "th-list",
              isExpanded: treeExpansion[0] === true,
              label: `${chamberLookup[capFirstLetter(chamber)]
                } ${billNumber} - ${billVersion.toUpperCase()}`,
              childNodes: children,
              className: "link",
            },
          ]);
        }
      );
    }
  }, [congress, chamber, billNumber, billVersion, treeExpansion]);
  function onExpand(node) {
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

export default withRouter(BillDiffSidebar);
