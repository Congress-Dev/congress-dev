import React, { useEffect, useState, useRef, useContext } from "react";
import lodash from "lodash";
import { useHistory } from "react-router-dom";
import {
    Callout,
    Section,
    SectionCard,
    Popover,
    Button,
} from "@blueprintjs/core";

import { BillContext, LoginContext } from "context";

import { chamberLookup, versionToFull } from "common/lookups";
import {
    getBill,
    getBill2,
    getBillSummary,
    getBillVersionTextv2,
} from "common/api";

import {
    BillDisplay,
    BillViewSidebar,
    BillViewToolbar,
    TalkToBill,
} from "components";

// Default bill versions to choose
// TODO: These should be enums
const defaultVers = {
    house: "IH",
    senate: "IS",
};

function BillViewer(props) {
    const { congress, chamber, billNumber, billVersion, uscTitle, uscSection } =
        props.match.params;

    const elementRef = useRef();
    const history = useHistory();

    // DEBUG: Just to make it easier to debug bills
    const { user } = useContext(LoginContext);

    // TODO: Add sidebar for viewing the differences that a bill will generate
    // TODO: Option for comparing two versions of the same bill and highlighting differences
    const [bill, setBill] = useState({});
    const [bill2, setBill2] = useState({});
    const [billSummary, setBillSummary] = useState([]);
    const [billEffective, setBillEffective] = useState(null);
    const [billVers, setBillVers] = useState(
        billVersion || defaultVers[chamber.toLowerCase()],
    );
    const [billVersId, setBillVersId] = useState(0);
    const [textTree, setTextTree] = useState({});
    const [treeLookup, setTreeLookup] = useState({});
    const [dateAnchors, setDateAnchors] = useState([]);

    useEffect(() => {
        const element = elementRef.current;
        if (element) {
            const yPosition = element.getBoundingClientRect().top + 135;
            document.documentElement.style.setProperty(
                "--bill-content-y-position",
                `${yPosition}px`,
            );
        }
    }, []);

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
                    setBillEffective(null);
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
        if (billVersId !== 0) {
            const url =
                `/bill/${congress}/${chamber}/${billNumber}/${billVers || billVersion}${diffStr}` +
                props.location.search +
                props.location.hash;

            if (url != window.location.pathname + window.location.hash) {
                props.history.push(url);
            }
            // Make sure to push the search and hash onto the url
            getBillVersionTextv2(billVersId).then(setTextTree);
        }
    }, [billVersId, billVers]);

    useEffect(() => {
        if (bill.legislation_versions == null) {
            return;
        }
        // If we didn't get a bill version, default to the introduced one.
        if (billVersion === undefined) {
            if (bill.legislation_versions !== undefined) {
                setBillVers(bill.legislation_versions[0].legislation_version);
                setBillVersId(
                    bill.legislation_versions[0].legislation_version_id,
                );
            } else {
                setBillVers(defaultVers[chamber.toLowerCase()]);
            }
        } else {
            lodash.forEach(bill.legislation_versions, (e) => {
                if (e.legislation_version === billVersion) {
                    setBillVersId(e.legislation_version_id);
                }
            });
        }
    }, [bill.legislation_versions]);

    useEffect(() => {
        if (bill.legislation_id) {
            getBill2(bill.legislation_id, billVers).then(setBill2);
        }
    }, [bill.legislation_id, billVers]);

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
        <BillContext.Provider
            value={{
                bill,
                bill2,
                billEffective,
                billNumber,
                billSummary,
                billVers,
                billVersion,
                chamber,
                congress,
                dateAnchors,
                scrollContentIdIntoView,
                setBillVers,
                textTree,
            }}
        >
            <Section
                className="page"
                title={bill.title}
                subtitle={
                    (user && user.userId === "mustyoshi@gmail.com"
                        ? `${billVersId} - `
                        : '') +
                    `${chamberLookup[bill.chamber]} ${bill.number}`
                }
            >
                <SectionCard>
                    <div className="sidebar">
                        <BillViewSidebar />
                    </div>

                    <Section
                        compact={true}
                        className="content"
                        title={versionToFull[billVers.toLowerCase()]}
                        subtitle={billEffective}
                        icon="drag-handle-vertical"
                        rightElement={<BillViewToolbar />}
                    >
                        <Callout>
                            <div className="bill-content" ref={elementRef}>
                                <BillDisplay />
                            </div>
                        </Callout>
                    </Section>
                </SectionCard>
            </Section>

            <Popover
                placement="top-end"
                position="top"
                content={
                    <>
                        <TalkToBill />
                    </>
                }
            >
                <Button className="chat-popover-trigger" icon="chat" />
            </Popover>
        </BillContext.Provider>
    );
}

export default BillViewer;
