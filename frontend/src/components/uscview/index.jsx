import React, { useEffect, useState } from "react";
import { useHistory, Link } from "react-router-dom";

import lodash from "lodash";

import { Spinner } from "@blueprintjs/core";

import { getUSCSectionContent } from "../../common/api";
import { md5 } from "../../common/other";

import { diffWords } from "diff";
import xmldoc from "xmldoc";

import "../../styles/usc-view.scss";

function USCView(props) {
    const history = useHistory();

    const [contentTree, setContentTree] = useState({});
    const [activeHash, setActiveHash] = useState(
        history.location.hash.slice(history.location.hash.lastIndexOf("#") + 1),
    );

    const [renderedTarget, setRenderedTarget] = useState(false);
    const { release, title, section, diffs = {} } = props;

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
                <span className={`usc-content-${style}`} key={ind}>
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
        if (str.includes("<") && str.includes(">")) {
            const parsed = new xmldoc.XmlDocument(`<str>${str}</str>`);
            return lodash.reduce(
                parsed.children,
                (prev, cur) => {
                    if (cur.text) {
                        return [...prev, cur.text];
                    } else if (cur.name === "usccite") {
                        return [
                            ...prev,
                            <Link
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
                    newItem[key] = diffStyle(
                        diffWords(
                            removeCitations(item[key] || ""),
                            removeCitations(itemDiff[key] || ""),
                        ),
                    );
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
        if (event.target.tagName.toLowerCase() !== "a") {
            history.replace({ hash: `#${goUpParentChain(event.target)}` });
            event.preventDefault();
            event.stopPropagation();
        }
    }
    function renderRecursive(node) {
        const newChildren = lodash
            .chain(node.children || [])
            .map(computeDiff)
            .sortBy("order_number")
            .value();
        return (
            <>
                {lodash.map(newChildren, (item, ind) => {
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
                                activeHash === itemHash
                                    ? "usc-content-hash"
                                    : ""
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
                            {renderRecursive({ children })}
                        </div>
                    );
                })}
            </>
        );
    }
    if (contentTree.loading) {
        return <Spinner intent="primary" />;
    }
    return <>{renderRecursive(contentTree)}</>;
}

export default USCView;
