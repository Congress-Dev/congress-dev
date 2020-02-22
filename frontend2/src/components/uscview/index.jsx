import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { getUSCSectionContent } from "common/api";
import SyncLoader from "react-spinners/SyncLoader";
import { diffWords } from "diff";

const styles = {
  section: {
    marginLeft: "20px",
    marginBottom: "0px",
  },
  "quoted-block": {
    borderWidth: "1px",
    borderStyle: "solid",
    borderColor: "gray",
    backgroundColor: "lightgray",
  },
  continue: {
    marginLeft: "20px",
    marginBottom: "0px",
    display: "block",
  },
  unchanged: {},

  added: {
    backgroundColor: "#cdffd8",
  },
  removed: {
    backgroundColor: "#ffdce0",
    textDecoration: "line-through",
    textDecorationColor: "#FF576B",
  },
  centered: {
    textAlign: "center",
  },
  col_a: {
    height: "90vh",
    overflowX: "wrap",
  },
  col: {
    height: "90vh",
    overflowX: "wrap",
  },
  sidebar: {},
};
function USCView(props) {
  const [contentTree, setContentTree] = useState({});
  const { release, title, section, diffs = {} } = props;
  console.log("View", props);
  useEffect(() => {
    if (section) {
      setContentTree({ loading: true });
      getUSCSectionContent(release, title, section).then(setContentTree);
    }
  }, [section]);
  function diffStyle(diffList) {
    return diffList.map((part, ind) => {
      let style = "unchanged";
      if (part.removed) {
        style = "removed";
      } else if (part.added) {
        style = "added";
      }
      return (
        <span className={style} style={styles[style]} key={ind}>
          {" "}
          {part.value}
        </span>
      );
    });
  }
  function computeDiff(item) {
    let newItem = Object.assign({}, item);
    const itemDiff = diffs[`${item.usc_content_id}`];
    if (itemDiff) {
      ["heading", "section_display", "content_str"].forEach(key => {
        if (itemDiff[key] !== undefined && itemDiff[key] !== item[key]) {
          newItem[key] = diffStyle(diffWords(item[key] || "", itemDiff[key] || ""));
          // TODO: Fix this ordering issue on the backend maybe?
          // Should create diffs to reorder things?
          newItem["order_number"] -= .01;
        }
      });
    }
    return newItem;
  }
  function renderRecursive(node) {
    const newChildren = lodash.chain(node.children || []).map(computeDiff).sortBy("order_number").value();
    return (
      <>
        {lodash.map(newChildren, (item, ind) => {
          const {
            usc_content_id,
            content_str,
            content_type,
            section_display,
            heading,
            children = [],
          } = item;
          return (
            <div
              name={usc_content_id}
              key={ind}
              style={
                content_type === "legis-body"
                  ? {}
                  : styles[content_type] || styles.section
              }
            >
              <span>
                {heading !== undefined ? (
                  <b>
                    {section_display} {heading}
                  </b>
                ) : (
                  <span style={{ fontWeight: "bolder" }}>{section_display} </span>
                )}
                <span style={heading !== undefined ? styles.continue : {}}>
                  {content_str}
                </span>
              </span>
              {renderRecursive({ children })}
            </div>
          );
        })}
      </>
    );
  }
  if (contentTree.loading) {
    return <SyncLoader loading={true} />;
  }
  return <>{renderRecursive(contentTree)}</>;
}

export default USCView;
