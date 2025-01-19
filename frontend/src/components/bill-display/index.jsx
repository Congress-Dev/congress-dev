import React, { useEffect, useState, useContext } from "react";
import { useHistory, Link } from "react-router-dom";
import lodash from "lodash";
import { Tooltip, Spinner } from "@blueprintjs/core";

import { md5 } from "common/other";
import { VALID_ACTIONS } from "common/enums";
import { getLongestString } from "common/utils";

import { BillContext, PreferenceContext, PreferenceEnum } from "context";

import "styles/actions.scss";
import "styles/bill-view.scss";

function BillDisplay() {
    const props = useContext(BillContext);
    const { preferences } = useContext(PreferenceContext);

    const actionParse = preferences[PreferenceEnum.HIGHLIGHT_ACTIONS];
    const dateParse = preferences[PreferenceEnum.HIGHLIGHT_DATES];
    const dollarParse = preferences[PreferenceEnum.HIGHLIGHT_DOLLARS];

    // TODO: Add minimap scrollbar
    // *TODO*: Start using the action list to render a list of parsed actions
    // TODO: Add permalink feature
    // TODO: Add highlight feature to permalink in the url ?link=a/1/ii&highlight=a/1/ii,a/1/v
    const history = useHistory();
    const textTree = props.textTree;
    const [activeHash, setActiveHash] = useState(
        (history.location.hash || "#").slice(1) || "",
    );

    const [renderedTarget, setRenderedTarget] = useState(false);

    useEffect(() => {
        // If we render the hash target, go ahead and zip it into view
        if (renderedTarget) {
            document.getElementById(activeHash).scrollIntoView();
        }
    }, [renderedTarget]);

    useEffect(() => {
        setActiveHash((history.location.hash || "#").slice(1) || "");
    }, [history.location.hash]);

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
    }

    function generateLinkToCite(citeLink) {
        const { congress, chamber, billNumber, billVersion } = props;
        const parts = citeLink.split("/");
        const itemHash = md5(citeLink.toLowerCase());
        if (parts.length > 4) {
            let paddedTitle = `00${parts[3].slice(1)}`;
            paddedTitle = paddedTitle.slice(
                Math.max(paddedTitle.lastIndexOf("0"), paddedTitle.length - 2),
            );
            return (
                <Link
                    to={`/bill/${congress}/${chamber}/${billNumber}/${billVersion}/diffs/${paddedTitle}/${parts[4].slice(
                        1,
                    )}#${itemHash}`}
                >
                    {citeLink}
                </Link>
            );
        } else {
            return null;
        }
    }

    function generateActionStr(action) {
        let actionStr = [];
        if (props.showActions === false) {
            return "";
        }
        let cite_link = "";
        lodash.forEach(action, (actionP) => {
            cite_link = getLongestString(actionP.parsed_cite || "", cite_link);
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
                lodash.forEach(actionP, (value, key) => {
                    if (key !== "REGEX") {
                        actionStr.push(
                            <span style={{ marginLeft: "5px" }}>
                                {" - "}
                                {key} = |{value}|
                            </span>,
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
    function generateCitationStr(citation) {
        let actionStr = [];
        if (props.showActions === false) {
            return "";
        }
        const keys = lodash
            .chain(citation)
            .keys()
            .filter((e) => {
                return !["changed", "parsed_cite", "cite_link"].includes(e);
            })
            .value();
        if (keys.length > 0) {
            actionStr.push(<span>{keys[0]}</span>);
            actionStr.push(<br />);
            lodash.forEach(citation, (value, key) => {
                if (key !== "REGEX") {
                    actionStr.push(
                        <span style={{ marginLeft: "5px" }}>
                            {" - "}
                            {key} = |{JSON.stringify(value)}|
                        </span>,
                    );
                    actionStr.push(<br />);
                }
            });
        }
        if (actionStr.length > 0) {
            return <>{actionStr}</>;
        }
        return "";
    }

    function generateActionHighlighting(contentStr, action) {
        if (actionParse === false) {
            return contentStr;
        }
        // We are looking at the action objects for items within it that represent the captured regex
        /*
    {
      "AMEND-MULTIPLE": {
        "REGEX": 1,
        "target": "Section 303(b)(1)(A)",
        "within": "the Help America Vote Act of 2002 (52 U.S.C. 21083(b)(1)(A))"
      },
      "changed": true,
      "cite_link": "/us/usc/t52/s21083/b/1/A",
      "diff_id": null,
      "parsed_cite": "/us/usc/t52/s21083/b/1/A"
    }
    */

        // Within each one we are using the VALID_ACTIONS list to pull out the action key "AMEND-MULTIPLE" in this case
        // And then these correspond to the regex groups we identify, except for the REGEX key, which we ignore
        // Using those substrings, we then highlight the next
        let strings = lodash
            .chain(action)
            .map(lodash.toPairs)
            .flatten()
            .sort()
            .value();
        let tempStr = contentStr;
        lodash.forEach(strings, (value) => {
            if (value[0] !== "REGEX") {
                tempStr = tempStr.replace(
                    value[1],
                    `<span class="action-${value[0]}">${value[1]}</span>`,
                );
                if (value[0] === "_full_match") {
                    return false;
                }
            }
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
                            actions,
                            children = [],
                        },
                        ind,
                    ) => {
                        const action = actions[0]?.actions[0] || {};
                        const citation = actions[0]?.citations[0] || {};
                        let summaryContent = lodash.find(
                            props.billSummary,
                            (e) => {
                                return (
                                    e.legislationContentId ===
                                    legislation_content_id
                                );
                            },
                        );
                        let summaryStr = summaryContent?.summary || "";
                        let actionStr = generateActionStr(action);
                        let citationStr = generateCitationStr(citation);
                        content_str = generateActionHighlighting(
                            content_str,
                            action,
                        );
                        const itemHash =
                            `${lc_ident || legislation_content_id}`.toLowerCase();
                        const outerClass = `content-${content_type} bill-content-section ${
                            activeHash !== "" && activeHash === itemHash
                                ? "content-hash"
                                : ""
                        }`;

                        let innerClass = "";

                        if (dateParse) {
                            const dateRegex =
                                /\b((?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec))\s*(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})\b/;
                            if (dateRegex.test(content_str)) {
                                innerClass += " content-date";
                            }
                        }

                        if (dollarParse) {
                            const dollarRegex = /\$\d{1,3}(,\d{3})*(\.\d{2})?/;
                            if (dollarRegex.test(content_str)) {
                                innerClass += " content-dollar";
                            }
                        }

                        if (
                            !renderedTarget &&
                            itemHash &&
                            activeHash &&
                            itemHash === activeHash
                        ) {
                            setRenderedTarget(true);
                        }

                        // TODO: Get rid of this if statement, with better CSS
                        if (heading != null) {
                            return (
                                <div
                                    id={itemHash}
                                    name={legislation_content_id}
                                    key={legislation_content_id}
                                    className={outerClass}
                                    onClick={changeUrl}
                                >
                                    <Tooltip
                                        content={
                                            <p style={{ maxWidth: "300px" }}>
                                                {summaryStr != "" ? (
                                                    <span>
                                                        <b>Summary:</b>{" "}
                                                        {summaryStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}

                                                {summaryStr != "" &&
                                                actionStr != "" ? (
                                                    <>
                                                        <br />
                                                        <br />
                                                    </>
                                                ) : (
                                                    ""
                                                )}

                                                {actionStr != "" ? (
                                                    <span>
                                                        <b>Actions:</b>{" "}
                                                        {actionStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}

                                                {citationStr != "" ? (
                                                    <span>
                                                        <b>Citations:</b>{" "}
                                                        {citationStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}
                                            </p>
                                        }
                                        disabled={
                                            actionStr === "" &&
                                            summaryStr === ""
                                        }
                                        isOpen={
                                            activeHash !== "" &&
                                            activeHash === itemHash
                                        }
                                    >
                                        <span>
                                            <b>
                                                {section_display} {heading}
                                            </b>
                                            <p
                                                className={
                                                    "bill-content-continue" +
                                                    innerClass
                                                }
                                            >
                                                {content_str}
                                            </p>
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
                                    key={legislation_content_id}
                                    className={outerClass}
                                    onClick={changeUrl}
                                >
                                    <Tooltip
                                        content={
                                            <p style={{ maxWidth: "300px" }}>
                                                {summaryStr != "" ? (
                                                    <span>
                                                        <b>Summary:</b>{" "}
                                                        {summaryStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}

                                                {summaryStr != "" &&
                                                actionStr != "" ? (
                                                    <>
                                                        <br />
                                                        <br />
                                                    </>
                                                ) : (
                                                    ""
                                                )}

                                                {actionStr != "" ? (
                                                    <span>
                                                        <b>Actions:</b>{" "}
                                                        {actionStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}
                                                {citationStr != "" ? (
                                                    <span>
                                                        <b>Citations:</b>{" "}
                                                        {citationStr}
                                                    </span>
                                                ) : (
                                                    ""
                                                )}
                                            </p>
                                        }
                                        disabled={
                                            actionStr === "" &&
                                            summaryStr === ""
                                        }
                                        isOpen={
                                            activeHash !== "" &&
                                            activeHash === itemHash
                                        }
                                    >
                                        {content_str != null && (
                                            <span>
                                                <span
                                                    className={
                                                        "bill-content-section-display"
                                                    }
                                                >
                                                    {section_display}
                                                </span>{" "}
                                                <span className={innerClass}>
                                                    {content_str}
                                                </span>
                                            </span>
                                        )}
                                    </Tooltip>
                                    {renderRecursive({ children })}
                                </div>
                            );
                        }
                    },
                )}
            </>
        );
    }

    if (
        textTree == null ||
        textTree.loading ||
        textTree.content_type !== "legis-body"
    ) {
        return <Spinner className="loading-spinner" intent="primary" />;
    }

    // TODO: Convert this to recursive components to speed up rerenders
    return <>{renderRecursive(props.textTree)}</>;
}

export default BillDisplay;
