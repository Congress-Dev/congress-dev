import React, { useEffect, useState, useContext } from "react";
import lodash from "lodash";
import { useHistory } from "react-router-dom";
import {
    Callout,
    Button,
    Drawer,
    Section,
    SectionCard,
} from "@blueprintjs/core";

import { ThemeContext } from "context";

import { chamberLookup, versionToFull } from "common/lookups";
import {
    getBill,
    getBill2,
    getBillSummary,
    getBillVersionTextv2,
} from "common/api";

import { BillDisplay, BillViewSidebar } from "components";

// Default bill versions to choose
// TODO: These should be enums
const defaultVers = {
    house: "IH",
    senate: "IS",
};

function BillViewer(props) {
    // TODO: Add sidebar for viewing the differences that a bill will generate
    // TODO: Option for comparing two versions of the same bill and highlighting differences
    const [bill, setBill] = useState({});
    const [bill2, setBill2] = useState({});
    const [textTree, setTextTree] = useState({});
    const [actionParse, setActionParse] = useState(false);

    const [dateAnchors, setDateAnchors] = useState([]);
    const [treeLookup, setTreeLookup] = useState({});
    const history = useHistory();
    const { congress, chamber, billNumber, billVersion, uscTitle, uscSection } =
        props.match.params;

    const [billVers, setBillVers] = useState(
        billVersion || defaultVers[chamber.toLowerCase()],
    );
    const [billEffective, setBillEffective] = useState(null);

    const [billSummary, setBillSummary] = useState([]);
    const [drawerOpen, setDrawerOpen] = useState(false);
    const { isDarkMode, setIsDarkMode } = useContext(ThemeContext);

    useEffect(() => {
        // If we didn't get a bill version, default to the introduced one.
        if (billVersion === undefined) {
            if (bill.legislation_versions !== undefined) {
                setBillVers(bill.legislation_versions[0].legislation_version);
            } else {
                setBillVers(defaultVers[chamber.toLowerCase()]);
            }
        } else {
            setBillVers(billVersion);
        }

        getBill(congress, chamber, billNumber)
            .then((response) => {
                const matchingVersion = lodash.find(
                    response.legislation_versions,
                    (e) => {
                        if (billVersion === undefined) {
                            return true;
                        } else {
                            return e.legislation_version === billVersion;
                        }
                    },
                );

                if (matchingVersion != null) {
                    getBillSummary(matchingVersion.legislation_version_id).then(
                        setBillSummary,
                    );
                    setBillEffective(matchingVersion.effective_date);
                } else {
                    setBillEffective(null)
                }

                return response;
            })
            .then(setBill);
    }, [props.location.pathname]);

    useEffect(() => {
        // When the user selects a new version, update the url
        // TODO: Update this to replace state when changing the bill version multiple times
        let diffStr = "";
        if (props.location.pathname.includes("diffs")) {
            diffStr = `/diffs/${uscTitle}/${uscSection}`;
        }
        if (billVers !== undefined) {
            const url =
                `/bill/${congress}/${chamber}/${billNumber}/${billVers || billVersion}${diffStr}` +
                props.location.search +
                props.location.hash;

            if (url != window.location.pathname + window.location.hash) {
                props.history.push(url);
            }
            // Make sure to push the search and hash onto the url
            getBillVersionTextv2(12088).then(
                setTextTree,
            );
        }
    }, [billVers]);

    useEffect(() => {
        if (bill.legislation_versions == null) {
            return;
        }
        // If we didn't get a bill version, default to the introduced one.
        if (billVersion === undefined) {
            if (bill.legislation_versions !== undefined) {
                setBillVers(bill.legislation_versions[0].legislation_version);
            } else {
                setBillVers(defaultVers[chamber.toLowerCase()]);
            }
        } else {
            const validVersions = lodash.map(
                bill.legislation_versions,
                "legislation_version",
            );
            if (!validVersions.includes(billVersion)) {
                setBillVers(validVersions[0]);
            } else {
                setBillVers(billVersion);
            }
        }
    }, [bill.legislation_versions]);

    useEffect(() => {
        if (bill.legislation_id) {
            getBill2(bill.legislation_id, billVersion).then(setBill2);
        }
    }, [bill.legislation_id, billVersion]);

    useEffect(() => {
        if (textTree == null) {
            return;
        }
        const newLookup = {};
        const _recursive = (node) => {
            newLookup[node.legislation_content_id] =
                `${node.lc_ident || node.legislation_content_id}`.toLowerCase();
            if (node.children === undefined) {
                return;
            }
            node.children.map(_recursive);
        };
        _recursive(textTree);
        setTreeLookup(newLookup);
    }, [textTree]);

    useEffect(() => {
        if (textTree == null) {
            return;
        }
        setDateAnchors(extractDates(textTree));
    }, [textTree]);

    const extractDates = function (_textTree) {
        const dateRegex =
            /(?:(?<month>(?:Jan|Febr)uary|March|April|May|Ju(?:ne|ly)|August|(?:Septem|Octo|Novem|Decem)ber) (?<day>\d\d?)\, (?<year>\d\d\d\d))/gim;
        let _dates = [];
        lodash.forEach(_textTree.children, (node) => {
            _dates = [..._dates, ...extractDates(node)];
        });
        const itemHash =
            `${_textTree.lc_ident || _textTree.legislation_content_id}`.toLowerCase();
        let m;
        while ((m = dateRegex.exec(_textTree.content_str)) !== null) {
            // This is necessary to avoid infinite loops with zero-width matches
            if (m.index === dateRegex.lastIndex) {
                dateRegex.lastIndex++;
            }
            _dates.push({ title: m[0], hash: itemHash });
        }

        return _dates;
    };

    const scrollContentIdIntoView = (contentId) => {
        if (treeLookup[contentId] !== undefined) {
            const ele = document.getElementById(treeLookup[contentId]);
            if (ele) {
                history.location.hash = treeLookup[contentId];
                ele.scrollIntoView();
            }
        }
    };

    return (
        <Section
            className="page"
            title={bill.title}
            subtitle={`${chamberLookup[bill.chamber]} ${bill.number}`}
        >
            {billSummary != null && billSummary[0] != null ? (
                <SectionCard>
                    <div className="section-detail">
                        <span className="section-detail-label">Summary:</span>
                        <span className="section-detail-value">
                            {billSummary[0].summary}
                        </span>
                    </div>
                </SectionCard>
            ) : (
                ""
            )}

            <SectionCard>
                <div className="sidebar no-mobile">
                    <BillViewSidebar
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVers={billVers}
                        bill={bill}
                        dateAnchors={dateAnchors}
                        bill2={bill2}
                        scrollContentIdIntoView={scrollContentIdIntoView}
                        setActionParse={setActionParse}
                        billVersion={billVersion}
                        setBillVers={setBillVers}
                        actionParse={actionParse}
                    />
                </div>
                <Drawer
                    className={isDarkMode ? "bp5-dark" : ""}
                    isOpen={drawerOpen}
                    onClose={() => setDrawerOpen(false)}
                    isCloseButtonShown={true}
                    title="Display Options"
                    lazy={false}
                >
                    <BillViewSidebar
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVers={billVers}
                        bill={bill}
                        dateAnchors={dateAnchors}
                        bill2={bill2}
                        scrollContentIdIntoView={scrollContentIdIntoView}
                        setActionParse={setActionParse}
                        billVersion={billVersion}
                        setBillVers={setBillVers}
                        actionParse={actionParse}
                    />
                </Drawer>
                <Section
                    className="content"
                    title={versionToFull[billVers.toLowerCase()]}
                    subtitle={billEffective}
                    compact={true}
                    icon="drag-handle-vertical"
                    rightElement={
                        <Button
                            className="bill-options mobile-flex"
                            icon="cog"
                            onClick={() => {
                                setDrawerOpen(true);
                            }}
                        />
                    }
                >
                    <Callout>
                        <BillDisplay
                            congress={congress}
                            chamber={chamber}
                            billNumber={billNumber}
                            billVersion={billVersion}
                            billSummary={billSummary}
                            textTree={textTree}
                            showActions={actionParse}
                        />
                    </Callout>
                </Section>
            </SectionCard>
        </Section>
    );
}

export default BillViewer;
