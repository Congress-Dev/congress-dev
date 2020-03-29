// Will have to handle fetching the bill text, and formatting it correctly.

import React, { useEffect, useState } from "react";
import lodash from "lodash";

import SyncLoader from "react-spinners/SyncLoader";
import { Tooltip } from "@blueprintjs/core";

import { getBillVersionText } from "common/api.js";
import "styles/actions.scss";
import "styles/bill-view.scss";

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
  function generateActionStr(action) {
    let actionStr = [];
    if (props.showTooltips === false) {
      return "";
    }
    lodash.forEach(action, actionP => {
      const keys = lodash
        .chain(actionP)
        .keys()
        .filter(e => {
          return !["changed", "parsed_cite"].includes(e);
        })
        .value();
      if (keys.length > 0) {
        actionStr.push(<span>{keys[0]}</span>);
        actionStr.push(<br />);
        lodash.forEach(actionP[keys[0]], (value, key) => {
          if (key !== "REGEX") {
            actionStr.push(
              <span style={{ marginLeft: "5px" }}>
                {" - "}
                {key} = |{value}|
              </span>
            );
            actionStr.push(<br />);
          }
        });
        // actionStr += items;
      }
      console.log(keys);
    });
    if (actionStr.length > 0) {
      return <>{actionStr}</>;
    }
    return "";
  }
  function generateActionHighlighting(contentStr, action) {
    if (props.showTooltips === false) {
      return contentStr;
    }
    const strings = lodash
      .chain(action)
      .map(lodash.toPairs)
      .flatten()
      .filter(x => !["changed", "parsed_cite"].includes(x[0]))
      .map(x => x[1])
      .map(lodash.toPairs)
      .flatten()
      .map(x => {
        return { [x[0]]: x[1] };
      })
      .reduce((s, x) => Object.assign(x, s), {})
      .value();
    let tempStr = contentStr;
    lodash.forEach(strings, (value, key) => {
      tempStr = tempStr.replace(value, `<span class="action-${key}">${value}</span>`);
    });
    console.log(tempStr);
    return (
      <span
        dangerouslySetInnerHTML={{
          __html: tempStr,
        }}
      />
    );
  }
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
            let actionStr = generateActionStr(action);
            content_str = generateActionHighlighting(content_str, action);
            if (heading !== undefined) {
              return (
                <div
                  name={legislation_content_id}
                  key={ind}
                  className={`bill-content-${content_type} bill-content-section`}
                >
                  <Tooltip
                    content={actionStr}
                    disabled={actionStr === "" || props.showTooltips !== true}
                  >
                    <span>
                      <b>
                        {section_display} {heading}
                      </b>
                      <p className={"bill-content-continue"}>{content_str}</p>
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
                  className={`bill-content-${content_type} bill-content-section`}
                >
                  <Tooltip
                    content={actionStr}
                    disabled={actionStr === "" || props.showTooltips !== true}
                  >
                    <span>
                      <span className={"bill-content-section-display"}>
                        {section_display}
                      </span>{" "}
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
