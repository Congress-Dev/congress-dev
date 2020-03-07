// Will have to handle fetching the bill text, and formatting it correctly.

import React, { useEffect, useState } from "react";
import lodash from "lodash";

import SyncLoader from "react-spinners/SyncLoader";
import { Tooltip } from "@blueprintjs/core";

import { getBillVersionText } from "common/api.js";

// TODO: move this somewhere in scss?
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
function BillDisplay(props) {
  // TODO: Add minimap scrollbar
  // *TODO*: Start using the action list to render a list of parsed actions
  // TODO: Add permalink feature
  // TODO: Add highlight feature to permalink in the url ?link=a/1/ii&highlight=a/1/ii,a/1/v
  const [textTree, setTextTree] = useState({});
  useEffect(() => {
    const { congress, chamber, billNumber, billVersion } = props;
    setTextTree({ loading: true });
    getBillVersionText(congress, chamber, billNumber, billVersion).then(setTextTree);
  }, [props.billVersion]);
  function renderRecursive(node) {
    return (
      <>
        {lodash.map(
          node.children || [],
          (
            {
              legislation_content_id,
              content_str,
              content_type,
              section_display,
              heading,
              action,
              children = [],
            },
            ind
          ) => {
            let actionStr = lodash.chain(action).map(lodash.keys).flatten().remove(x=>x!=="changed"&&x!=="parsed_cite").value().join(", ");
            if (heading !== undefined) {
              return (
                <div
                  name={legislation_content_id}
                  key={ind}
                  style={
                    content_type === "legis-body"
                      ? {}
                      : styles[content_type] || styles.section
                  }
                >
                  <Tooltip content={actionStr} disabled={actionStr === "" || props.showTooltips !== true}>
                    <span>
                      <b>
                        {section_display} {heading}
                      </b>
                      <p style={styles.continue}>{content_str}</p>
                    </span>
                  </Tooltip>
                  {renderRecursive({ children })}
                </div>
              );
            } else {
              return (
                <div
                  name={legislation_content_id}
                  key={ind}
                  style={
                    content_type === "legis-body"
                      ? {}
                      : styles[content_type] || styles.section
                  }
                >
                  <Tooltip content={actionStr} disabled={actionStr === "" || props.showTooltips !== true}>
                    <span>
                      <span style={{ fontWeight: "bolder" }}>{section_display}</span>{" "}
                      <span>{content_str}</span>
                    </span>
                  </Tooltip>
                  {renderRecursive({ children })}
                </div>
              );
            }
          }
        )}
      </>
    );
  }
  if (textTree.loading) {
    return <SyncLoader loading={true} />;
  }
  return <>{renderRecursive(textTree)}</>;
}

export default BillDisplay;
