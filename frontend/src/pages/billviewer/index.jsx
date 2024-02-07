import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { Checkbox, Tabs, Tab } from "@blueprintjs/core";

import { getBillSummary, getBillSummary2, getBillVersionDiffForSection, getBillVersionText } from "../../common/api.js";

import BillDisplay from "../../components/billdisplay";
import BillDiffSidebar from "../../components/billdiffsidebar";
import BillViewAnchorList from "../../components/billviewanchorlistcomp";
import USCView from "../../components/uscview";


// AppropriationItem component to display individual appropriation details
const AppropriationItem = ({ appropriation, onNavigate }) => {
  // Function to handle click events
  const handleClick = () => {
    // This function could navigate to the specific clause in the legislation
    // For example, by setting the window's location hash to an anchor tag or by using a router navigation method
    onNavigate(appropriation.legislationContentId);
  };

  return (
    <div className="appropriation-item" onClick={handleClick}>
      <h4>Appropriation #{appropriation.appropriationId}</h4>
      <p>Amount: ${appropriation.amount.toLocaleString()}</p>
      {appropriation.newSpending && <p>New Spending</p>}
      {appropriation.fiscalYears.length > 0 && (
        <p>Fiscal Years: {appropriation.fiscalYears.join(', ')}</p>
      )}
      {appropriation.expirationYear && <p>Expires: {appropriation.expirationYear}</p>}
      <p>Until Expended: {appropriation.untilExpended ? 'Yes' : 'No'}</p>
    </div>
  );
};
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
  const [diffs, setDiffs] = useState({});
  const [textTree, setTextTree] = useState({});
  const [actionParse, setActionParse] = useState(false);
  const [selectedTab, setSelectedTab] = useState("ud");
  const [dateAnchors, setDateAnchors] = useState([]);
  const [dollarAnchors, setDollarAnchors] = useState([]);
  const [treeLookup, setTreeLookup] = useState({});
  const [diffMode, setDiffMode] = useState(false);
  const {
    congress,
    chamber,
    billNumber,
    billVersion,
    uscTitle,
    uscSection,
  } = props.match.params;

  const [billVers, setBillVers] = useState(
    billVersion || defaultVers[chamber.toLowerCase()]
  );
  useEffect(() => {
    // Grab the info from the rest API

    if (props.location.pathname.includes("diffs")) {
      setDiffMode(true);
      getBillVersionDiffForSection(
        congress,
        chamber,
        billNumber,
        billVersion,
        uscTitle,
        uscSection
      ).then(setDiffs);
    } else {
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
      setDiffMode(false);
    }
    getBillSummary(congress, chamber, billNumber).then(setBill);
  }, [props.location.pathname]);
  useEffect(() => {
    // When the user selects a new version, update the url
    // TODO: Update this to replace state when changing the bill version multiple times
    let diffStr = "";
    if (props.location.pathname.includes("diffs")) {
      diffStr = `/diffs/${uscTitle}/${uscSection}`;
    }
    if (billVers !== undefined) {
      // Make sure to push the search and hash onto the url
      props.history.push(
        `/bill/${congress}/${chamber}/${billNumber}/${billVers || billVersion
        }${diffStr}` +
        props.location.search +
        props.location.hash
      );
      getBillVersionText(congress, chamber, billNumber, billVers).then(setTextTree);
    }
  }, [billVers]);
  useEffect(() => {
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
        "legislation_version"
      );
      if (!validVersions.includes(billVersion)) {
        setBillVers(validVersions[0]);
      } else {
        setBillVers(billVersion);
      }
    }
  }, [bill.legislation_versions]);
  useEffect(() => {
    console.log(bill)
    getBillSummary2(bill.legislation_id).then(setBill2);
  }, [bill.legislation_id])
  useEffect(() => {
    const newLookup = {};
    const _recursive = (node) => {
      newLookup[node.legislation_content_id] = `${node.lc_ident || node.legislation_content_id}`.toLowerCase();
      if (node.children === undefined) {
        return;
      }
      node.children.map(_recursive);
    }
    _recursive(textTree);
    setTreeLookup(newLookup);
    console.log(newLookup);
  }, [textTree]);
  const extractDatesAndDollars = function (_textTree) {
    const dateRegex = /(?:(?<month>(?:Jan|Febr)uary|March|April|May|Ju(?:ne|ly)|August|(?:Septem|Octo|Novem|Decem)ber) (?<day>\d\d?)\, (?<year>\d\d\d\d))/gmi;
    const dollarRegex = /(?<dollar>\$\s?(\,?\d{1,3})(\,?\d{3})*(\.\d\d)?)/gmi;
    let _dates = [];
    let _dollars = [];
    lodash.forEach(_textTree.children, (node) => {
      const { dates, dollars } = extractDatesAndDollars(node);
      _dates = [..._dates, ...dates];
      _dollars = [..._dollars, ...dollars];
    });
    const itemHash = `${_textTree.lc_ident || _textTree.legislation_content_id}`.toLowerCase();
    let m;
    while ((m = dateRegex.exec(_textTree.content_str)) !== null) {
      // This is necessary to avoid infinite loops with zero-width matches
      if (m.index === dateRegex.lastIndex) {
        dateRegex.lastIndex++;
      }
      _dates.push([m[0], itemHash]);
    }
    while ((m = dollarRegex.exec(_textTree.content_str)) !== null) {
      // This is necessary to avoid infinite loops with zero-width matches
      if (m.index === dollarRegex.lastIndex) {
        dollarRegex.lastIndex++;
      }
      _dollars.push([m[0], itemHash]);
    }

    return { dates: _dates, dollars: _dollars };
  }
  useEffect(() => {
    const { dates, dollars } = extractDatesAndDollars(textTree);
    setDateAnchors(dates);
    setDollarAnchors(dollars);
  }, [textTree]);
  const scrollContentIdIntoView = (contentId) => {
    console.log(treeLookup, contentId, treeLookup[contentId])
    if (treeLookup[contentId] !== undefined) {
      const ele = document.getElementById(treeLookup[contentId]);
      if (ele) {
        ele.scrollIntoView();
      }
    }
  }
  return (
    <>
      <h3>{bill.title}</h3>Selected Version:{" "}
      <select
        id="bill-version-select"
        value={(billVers || "").toUpperCase()}
        onChange={(e) => setBillVers(e.target.value)}
        className="bp3"
      >
        {lodash.map(
          bill.legislation_versions,
          ({ legislation_version, effective_date }, ind) => {
            return (
              <option value={legislation_version} key={`bill-version-select-${ind}`}>
                {legislation_version}
                {effective_date !== "None" ? ` - ${effective_date}` : null}
              </option>
            );
          }
        )}
      </select>
      <br />
      <Checkbox
        label="Show action parsing details"
        value={actionParse}
        onClick={() => setActionParse(!actionParse)}
      />
      <hr />
      <Tabs className="sidebar" id="sidebar-tabs" selectedTabId={selectedTab} onChange={setSelectedTab}>
        <Tab
          id="ud"
          title="USCode Diffs"
          panel={<BillDiffSidebar
            congress={congress}
            chamber={chamber}
            billNumber={billNumber}
            billVersion={billVers || billVersion}
          />}
        />
        <Tab
          id="datelist"
          title="Dates"
          panel={<BillViewAnchorList
            anchors={dateAnchors}
            congress={congress}
            chamber={chamber}
            billNumber={billNumber}
            billVersion={billVersion}
          />}
        />
        {bill2 && bill2.appropriations && (
          <Tab
            id="dollarlist"
            title="Dollars"
            panel={<>{bill2.appropriations.map((app) => <AppropriationItem appropriation={app} onNavigate={scrollContentIdIntoView} />)}</>}
          />
        )}

      </Tabs>
      <div className="content">
        {diffMode === true ? (
          <USCView
            release={bill.usc_release_id || "latest"}
            section={uscSection}
            title={uscTitle}
            diffs={diffs}
          />
        ) : (
          <BillDisplay
            congress={congress}
            chamber={chamber}
            billNumber={billNumber}
            billVersion={billVersion}
            textTree={textTree}
            showTooltips={actionParse}
          />
        )}
      </div>
    </>
  );
}

export default BillViewer;
