import React, { useEffect, useState } from "react";
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
} from "@blueprintjs/core";

import { chamberLookup } from "common/lookups";
import {
    getBill,
    getBill2,
    getBillSummary,
    getBillVersionText,
} from "common/api";

import {
    AppropriationTree,
    BillDisplay,
    BillDiffSidebar,
    BillViewAnchorList,
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
    const [selectedTab, setSelectedTab] = useState("bill");
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

    function renderSidebar() {
        return <Tabs
            id="sidebar-tabs"
            selectedTabId={selectedTab}
            onChange={setSelectedTab}
        >
            <Tab
                id="bill"
                title="Bill"
                panel={
                    <>
                        <FormGroup
                            label="Version:"
                            labelFor="bill-version-select"
                        >
                            <HTMLSelect
                                id="bill-version-select"
                                value={(billVers || "").toUpperCase()}
                                onChange={(e) =>
                                    setBillVers(e.currentTarget.value)
                                }
                                className="bp3"
                                options={lodash.map(
                                    bill.legislation_versions,
                                    (
                                        {
                                            legislation_version,
                                            effective_date,
                                        },
                                        ind,
                                    ) => {
                                        return {
                                            label: `${legislation_version} ${effective_date !== "None" ? ` - ${effective_date}` : ""}`,
                                            value: legislation_version,
                                        };
                                    },
                                )}
                            />
                        </FormGroup>

                        <FormGroup label="Display Options:">
                            <Switch
                                label="Highlight dates"
                                value={actionParse}
                                onClick={() =>
                                    setActionParse(!actionParse)
                                }
                            />
                            <Switch
                                label="Highlight spending"
                                value={actionParse}
                                onClick={() =>
                                    setActionParse(!actionParse)
                                }
                            />
                            <Switch
                                label="Highlight tags"
                                value={actionParse}
                                onClick={() =>
                                    setActionParse(!actionParse)
                                }
                            />
                            <Switch
                                label="Action parsing details"
                                value={actionParse}
                                onClick={() =>
                                    setActionParse(!actionParse)
                                }
                            />
                        </FormGroup>
                    </>
                }
            />
            <Tab
                id="ud"
                title="USCode"
                panel={
                    <BillDiffSidebar
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVersion={billVers || billVersion}
                        bill={bill}
                    />
                }
            />
            <Tab
                id="datelist"
                title="Dates"
                panel={
                    <BillViewAnchorList
                        anchors={dateAnchors}
                        congress={congress}
                        chamber={chamber}
                        billNumber={billNumber}
                        billVersion={billVersion}
                    />
                }
            />
            {bill2 &&
                bill2.appropriations &&
                bill2.appropriations.length > 0 && (
                    <Tab
                        id="dollarlist"
                        title="Dollars"
                        panel={
                            <AppropriationTree
                                appropriations={bill2.appropriations}
                                onNavigate={scrollContentIdIntoView}
                            />
                        }
                    />
                )}
        </Tabs>
    }

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
                    setDrawerOpen(true)
                }}
            />
            <h1>
                {`${chamberLookup[bill.chamber]} ${bill.number}`} - {bill.title}
            </h1>

            {billSummary != null && billSummary[0] != null ? (
                <p>
                    {billSummary[0].summary}
                    <br />
                    <br />
                </p>
            ) : (
                ""
            )}

            <Divider />

            <div className="sidebar no-mobile">
                {renderSidebar()}
            </div>

            <Drawer
                className={"bp5-dark"}
                isOpen={drawerOpen}
                onClose={() => setDrawerOpen(false)}
                isCloseButtonShown={true}
                title="Display Options"
            >
                {renderSidebar()}
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
