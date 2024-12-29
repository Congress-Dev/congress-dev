import React, { useEffect, useState, useContext } from "react";
import lodash from "lodash";
import { useHistory } from "react-router-dom";
import {
    HTMLSelect,
    Switch,
    Callout,
    Button,
    Tabs,
    Tab,
    Card,
    Divider,
    Drawer,
    FormGroup,
    CompoundTag,
} from "@blueprintjs/core";

import { ThemeContext } from "context";

import { chamberLookup, partyLookup } from "common/lookups";
import {
    getBill,
    getBill2,
    getBillSummary,
    getBillVersionText,
} from "common/api";

import {
    BillDisplay,
    BillViewSidebar,
    BillVersionsBreadcrumb,
} from "components";

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
            getBillVersionText(congress, chamber, billNumber, billVers).then(
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
        <Card className="page">
            <Button
                className="congress-link"
                icon="share"
                onClick={() => {
                    window.open(
                        `https://congress.gov/bill/${bill.congress}-congress/${bill.chamber}-bill/${bill.number}`,
                        "_blank",
                    );
                }}
            />
            <Button
                className="bill-options mobile-flex"
                icon="menu"
                onClick={() => {
                    setDrawerOpen(true);
                }}
            />
            <h1>
                {`${chamberLookup[bill.chamber]} ${bill.number}`} - {bill.title}
            </h1>

            <span className="bill-card-introduced-date">
                <span style={{ fontWeight: "bold" }}>Introduced:</span>{" "}
                {bill.legislation_versions != null
                    ? bill.legislation_versions[0].effective_date
                    : ""}
            </span>
            <br/>
            {bill2?.sponsor != null ? (
                <>
                    <span style={{ fontWeight: "bold" }}>Sponsor:</span>{" "}
                    <CompoundTag
                        intent={bill2.sponsor.party == "Republican" ? "danger" : (bill2.sponsor.party == "Democrat" ? 'primary' : 'none')}
                        leftContent={partyLookup[bill2.sponsor.party] != null ? partyLookup[bill2.sponsor.party] : bill2.sponsor.party}
                    >
                        &nbsp;{bill2.sponsor.lastName}, {bill2.sponsor.firstName}&nbsp;
                    </CompoundTag>
                    <br />
                </>
            ) : ("")}

            <span style={{ fontWeight: "bold" }}>Versions:</span>{" "}
            <BillVersionsBreadcrumb bill={bill} />
            <br />
            {billSummary != null && billSummary[0] != null ? (
                <p>
                    <span style={{ fontWeight: "bold" }}>Summary:</span>{" "}
                    {billSummary[0].summary}
                    <br />
                    <br />
                </p>
            ) : (
                ""
            )}
            <Divider />
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
            <div className="content">
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
            </div>
        </Card>
    );
}

export default BillViewer;
