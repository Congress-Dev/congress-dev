// Will have to handle fetching the bill text, and formatting it correctly.

import React, { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";

import lodash from "lodash";

import SyncLoader from "react-spinners/SyncLoader";
import { Tooltip } from "@blueprintjs/core";

import { md5 } from "common/other";

import { getBillVersionText } from "common/api.js";
import "styles/actions.scss";
import "styles/bill-view.scss";

function BillDisplay(props) {
  // TODO: Add minimap scrollbar
  // *TODO*: Start using the action list to render a list of parsed actions
  // TODO: Add permalink feature
  // TODO: Add highlight feature to permalink in the url ?link=a/1/ii&highlight=a/1/ii,a/1/v
  const history = useHistory();

  const [textTree, setTextTree] = useState({});
  const [activeHash, setActiveHash] = useState(
    (history.location.hash || "#").slice(1) || ""
  );

  const [renderedTarget, setRenderedTarget] = useState(false);

  console.log(activeHash);
  useEffect(() => {
    // If we render the hash target, go ahead and zip it into view
    if (renderedTarget) {
      document.getElementById(activeHash).scrollIntoView();
    }
  }, [renderedTarget]);

  useEffect(() => {
    const { congress, chamber, billNumber, billVersion } = props;
    setTextTree({ loading: true });
    getBillVersionText(congress, chamber, billNumber, billVersion).then(setTextTree);
  }, [props.billVersion]);

  function goUpParentChain(element) {
    if (
      element &&
      element.className.indexOf("bill-content-section") > -1 &&
      element.id !== ""
    ) {
      setActiveHash(element.id);
      return element.id;
    } else if (element) {
      return goUpParentChain(element.parentElement);
    }
    return "";
  }

  function changeUrl(event) {
    history.replace({ hash: `#${goUpParentChain(event.target)}` });
    event.preventDefault();
    event.stopPropagation();
  }
  function generateLinkToCite(citeLink) {
    const { congress, chamber, billNumber, billVersion } = props;
    const parts = citeLink.split("/");
    const itemHash = md5(citeLink.toLowerCase());
    if (parts.length > 4) {
      let paddedTitle = `00${parts[3].slice(1)}`;
      paddedTitle = paddedTitle.slice(
        Math.max(paddedTitle.lastIndexOf("0"), paddedTitle.length - 2)
      );
      return (
        <a
          href={`/bill/${congress}/${chamber}/${billNumber}/${billVersion}/diffs/${paddedTitle}/${parts[4].slice(
            1
          )}#${itemHash}`}
        >
          {citeLink}
        </a>
      );
    } else {
      return null;
    }
  }
  function getLongest(str1, str2) {
    if (str1.length > str2.length) {
      return str1;
    }
    return str2;
  }
  function generateActionStr(action) {
    let actionStr = [];
    if (props.showTooltips === false) {
      return "";
    }
    let cite_link = "";
    lodash.forEach(action, (actionP) => {
      cite_link = getLongest(actionP.parsed_cite || "", cite_link);
      const keys = lodash
        .chain(actionP)
        .keys()
        .filter((e) => {
          return !["changed", "parsed_cite", "cite_link"].includes(e);
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
      }
    });
    if (actionStr.length > 0) {
      return (
        <>
          {actionStr}
          {generateLinkToCite(cite_link)}
        </>
      );
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
      .filter((x) => !["changed", "parsed_cite"].includes(x[0]))
      .map((x) => x[1])
      .map(lodash.toPairs)
      .flatten()
      .map((x) => {
        return { [x[0]]: x[1] };
      })
      .reduce((s, x) => Object.assign(x, s), {})
      .value();
    let tempStr = contentStr;
    lodash.forEach(strings, (value, key) => {
      tempStr = tempStr.replace(value, `<span class="action-${key}">${value}</span>`);
    });
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
              lc_ident,
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
            const itemHash = (lc_ident || "").toLowerCase();
            const outerClass = `bill-content-${content_type} bill-content-section ${
              activeHash !== "" && activeHash === itemHash ? "usc-content-hash" : ""
            }`;
            if (!renderedTarget && itemHash && activeHash && itemHash === activeHash) {
              setRenderedTarget(true);
            }
            // TODO: Get rid of this if statement, with better CSS
            if (heading !== undefined) {
              return (
                <div
                  id={itemHash}
                  name={legislation_content_id}
                  key={ind}
                  className={outerClass}
                  onClick={changeUrl}
                >
                  <Tooltip
                    content={actionStr}
                    disabled={actionStr === "" || props.showTooltips !== true}
                    isOpen={activeHash !== "" && activeHash === itemHash}
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
                  id={itemHash}
                  name={legislation_content_id}
                  key={ind}
                  className={outerClass}
                  onClick={changeUrl}
                >
                  <Tooltip
                    content={actionStr}
                    disabled={actionStr === "" || props.showTooltips !== true}
                    isOpen={activeHash !== "" && activeHash === itemHash}
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
