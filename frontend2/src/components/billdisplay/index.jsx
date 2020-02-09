// Will have to handle fetching the bill text, and formatting it correctly.

import React, { useEffect, useState } from "react";
import lodash from "lodash";

import SyncLoader from "react-spinners/SyncLoader";

import { getBillVersionText } from "common/api.js";

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
              children = [],
            },
            ind
          ) => {
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
                  <span>
                    <b>
                      {section_display} {heading}
                    </b>
                    <p style={styles.continue}>{content_str}</p>
                  </span>
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
                  <span>
                    <span style={{ fontWeight: "bolder" }}>{section_display}</span>{" "}
                    <span>{content_str}</span>
                  </span>
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
  return <>{renderRecursive(textTree)} </>;
}

export default BillDisplay;
