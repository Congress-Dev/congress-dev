import React, { useEffect, useState } from "react";
import { useHistory, Link } from "react-router-dom";
import lodash from "lodash";
import { diffWordsWithSpace } from "diff";
import xmldoc from "xmldoc";
import { Spinner } from "@blueprintjs/core";

import { getUSCSectionContent } from "common/api";
import { md5 } from "common/other";

import "styles/usc-view.scss";
function findCommonPrefix(str1, str2) {
    let i = 0;
    if (str1 === undefined || str2 === undefined) {
        return 0;
    }
    const minLength = Math.min(str1.length, str2.length);
    while (i < minLength && str1[i] === str2[i]) {
        i++;
    }
    if (str1[i] !== " " && i > 0 && str1[i - 1] === " ") {
        i--;
    }
    return i;
}

function findCommonSuffix(str1, str2) {
    let i = 0;
    if (str1 === undefined || str2 === undefined) {
        return 0;
    }
    const minLength = Math.min(str1.length, str2.length);
    while (
        i < minLength &&
        str1[str1.length - 1 - i] === str2[str2.length - 1 - i]
    ) {
        i++;
    }
    return i;
}

function findDiffStrings(str1, str2, maxSuffixLen = 0) {
    const words1 = str1.split(" ");
    const words2 = str2.split(" ");

    const minLength = Math.min(words1.length, words2.length);
    const differences = [];
    let start = null;
    let end = 0;
    for (let i = 0; i < minLength; i++) {
        if (words1[i] !== words2[i]) {
            if (start === null) {
                start = i;
            }
            end = i;
        } else {
            if (start !== null) {
                differences.push([start, end]);
                start = null;
            }
        }
    }

    if (start !== null) {
        differences.push([start, end]);
    }

    // Ensure there are at least 3 words between separate differences
    const filteredDifferences = [];
    for (let i = 0; i < differences.length; i++) {
        if (i === 0 || differences[i][0] - differences[i - 1][1] > 3) {
            filteredDifferences.push(differences[i]);
        }
    }

    return filteredDifferences;
}
function USCView({
    release,
    title,
    section,
    diffs = {},
    interactive = true,
    depth = 0,
    lines = 0,
}) {
  let lineCount = 0;
    const history = useHistory();

    const [contentTree, setContentTree] = useState({});
    const [activeHash, setActiveHash] = useState(
        history.location.hash.slice(history.location.hash.lastIndexOf("#") + 1),
    );

    const [renderedTarget, setRenderedTarget] = useState(false);

    useEffect(() => {
        if (renderedTarget) {
            document.getElementById(activeHash).scrollIntoView();
        }
    }, [renderedTarget]);

    useEffect(() => {
        if (section) {
            setContentTree({ loading: true });
            getUSCSectionContent(release, title, section).then(setContentTree);
        }
    }, [release, title, section]);

    function diffStyle(diffList) {
        return diffList.map((part, ind) => {
            let style = "unchanged";
            if (part.removed) {
                style = "removed";
            } else if (part.added) {
                style = "added";
            }
            return (
                <span className={`content-${style}`} key={ind}>
                    {" "}
                    {part.value}
                </span>
            );
        });
    }

    function removeCitations(str) {
        return str
            .replace(/\<usccite src.*?\"\>/g, "")
            .replace(/\<\/usccite\>/g, "");
    }

    function resolveCitations(str) {
        if (!str) {
            return str;
        }
        let index = 0;
        if (str.includes("<") && str.includes(">")) {
            const parsed = new xmldoc.XmlDocument(
                `<str>${str
                    .replace(/[\n\r]/g, "\\n")
                    .replace(/&/g, "&amp;")
                    .replace(/-/g, "&#45;")}</str>`,
            );
            return lodash.reduce(
                parsed.children,
                (prev, cur) => {
                    index++;
                    if (cur.text) {
                        return [...prev, cur.text];
                    } else if (cur.name === "usccite") {
                        return [
                            ...prev,
                            <Link
                                key={index}
                                to={`/uscode/${release}/${cur.attr.src.replace("/usc/", "")}`}
                            >
                                {cur.val}
                            </Link>,
                        ];
                    } else {
                        return [...prev, "[REMOVED]"];
                    }
                },
                [],
            );
        }
        return str;
    }

    function computeDiff(item) {
        let newItem = Object.assign({}, item);
        const itemDiff = diffs[`${item.usc_content_id}`];
        if (itemDiff) {
            ["heading", "section_display", "content_str"].forEach((key) => {
                if (
                    itemDiff[key] !== undefined &&
                    itemDiff[key] !== item[key]
                ) {
                    const diffStart = findCommonPrefix(
                        item[key],
                        itemDiff[key],
                    );
                    const diffEnd = findCommonSuffix(item[key], itemDiff[key]);

                    // Generate the diff
                    // The common prefix will be unchanged
                    // Removed text will be in red
                    // Added text will be in green
                    newItem[key] = diffStyle([
                        {
                            value: item[key]?.slice(0, diffStart) || "",
                            removed: false,
                            added: false,
                        },
                        {
                            value:
                                item[key]?.slice(
                                    diffStart + 1,
                                    item[key].length - diffEnd,
                                ) || "",
                            removed: true,
                            added: false,
                        },
                        {
                            value:
                                itemDiff[key]?.slice(
                                    diffStart,
                                    itemDiff[key].length - diffEnd,
                                ) || "",
                            removed: false,
                            added: true,
                        },
                        {
                            value:
                                itemDiff[key]?.slice(
                                    itemDiff[key].length - diffEnd,
                                ) || "",
                            removed: false,
                            added: false,
                        },
                    ]);
                    // TODO: Fix this ordering issue on the backend maybe?
                    // Should create diffs to reorder things?
                    newItem["order_number"] -= 0.01;
                }
            });
        } else {
            newItem.content_str = resolveCitations(newItem.content_str);
        }
        return newItem;
    }

    function goUpParentChain(element) {
        if (
            element.className.indexOf("usc-content-section") > -1 &&
            element.id !== ""
        ) {
            setActiveHash(element.id);
            return element.id;
        }
        return goUpParentChain(element.parentElement);
    }

    function changeUrl(event) {
        if (interactive && event.target.tagName.toLowerCase() !== "a") {
            history.replace({ hash: `#${goUpParentChain(event.target)}` });
            event.preventDefault();
            event.stopPropagation();
        }
    }

    function renderRecursive(node, rDepth = 0) {
        if (depth && rDepth > depth) {
            return null;
        }
        const newChildren = lodash
            .chain(node.children || [])
            .map(computeDiff)
            .sortBy("order_number")
            .value();
        return (
            <>
                {lodash.map(newChildren, (item, ind) => {
                  lineCount++;
                  if (lines && lineCount > lines) {
                    return null;
                  }
                    const {
                        usc_content_id,
                        usc_ident,
                        content_str,
                        content_type,
                        section_display,
                        heading,
                        children = [],
                    } = item;
                    const correctedType = content_type.slice(
                        content_type.indexOf("}") + 1,
                    );
                    const itemHash = md5(usc_ident.toLowerCase());
                    if (
                        !renderedTarget &&
                        itemHash &&
                        activeHash &&
                        itemHash === activeHash
                    ) {
                        setRenderedTarget(true);
                    }
                    return (
                        <div
                            id={itemHash}
                            name={usc_content_id}
                            className={`usc-content-${correctedType} usc-content-section ${
                                activeHash === itemHash ? "content-hash" : ""
                            }`}
                            key={ind}
                            onClick={changeUrl}
                        >
                            <span>
                                {heading !== undefined ? (
                                    <b>
                                        {section_display} {heading}
                                    </b>
                                ) : (
                                    <span
                                        className={
                                            "usc-content-section-display"
                                        }
                                    >
                                        {section_display}{" "}
                                    </span>
                                )}
                                <span
                                    className={
                                        heading !== undefined
                                            ? "usc-content-continue"
                                            : ""
                                    }
                                >
                                    {content_str}
                                </span>
                            </span>
                            {renderRecursive({ children}, rDepth + 1)}
                        </div>
                    );
                })}
            </>
        );
    }

    if (contentTree === undefined || contentTree?.loading) {
        return <Spinner intent="primary" />;
    }
    return <>{renderRecursive(contentTree)}</>;
}

export default USCView;
