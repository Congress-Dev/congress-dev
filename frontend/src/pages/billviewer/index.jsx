import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { useHistory } from "react-router-dom";
import { HTMLTable, HTMLSelect, Switch, Tag, Callout, Button, Tabs, Tab, Card, Divider, FormGroup } from "@blueprintjs/core";

import { chamberLookup } from "../../common/lookups";
import { getBillSummary, getBillSummary2, getBillVersionDiffForSection, getBillVersionText } from "../../common/api.js";

import AppropriationTree from "../../components/appropriationtree/index.js";
import BillDisplay from "../../components/billdisplay";
import BillDiffSidebar from "../../components/billdiffsidebar";
import BillViewAnchorList from "../../components/billviewanchorlistcomp";
import USCView from "../../components/uscview";

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
  const [selectedTab, setSelectedTab] = useState("bill");
  const [dateAnchors, setDateAnchors] = useState([]);
  const [treeLookup, setTreeLookup] = useState({});
  const [diffMode, setDiffMode] = useState(false);
  const history = useHistory();
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
      ).then(setDiffs)
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
      const url = `/bill/${congress}/${chamber}/${billNumber}/${billVers || billVersion}${diffStr}` +
        props.location.search +
        props.location.hash

      if(url != window.location.pathname + window.location.hash) {
        props.history.push(url);
      }
      // Make sure to push the search and hash onto the url
      getBillVersionText(congress, chamber, billNumber, billVers).then(setTextTree);
    }
  }, [billVers]);
  useEffect(() => {
    if(bill.legislation_versions == null) {
      return
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
    if (bill.legislation_id) {
      getBillSummary2(bill.legislation_id, billVersion).then(setBill2);
    }
  }, [bill.legislation_id, billVersion])
  useEffect(() => {
    if(textTree == null) {
      return
    }
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
  }, [textTree]);
  const extractDates = function (_textTree) {
    const dateRegex = /(?:(?<month>(?:Jan|Febr)uary|March|April|May|Ju(?:ne|ly)|August|(?:Septem|Octo|Novem|Decem)ber) (?<day>\d\d?)\, (?<year>\d\d\d\d))/gmi;
    let _dates = [];
    lodash.forEach(_textTree.children, (node) => {
      _dates = [..._dates, ...extractDates(node)];
    });
    const itemHash = `${_textTree.lc_ident || _textTree.legislation_content_id}`.toLowerCase();
    let m;
    while ((m = dateRegex.exec(_textTree.content_str)) !== null) {
      // This is necessary to avoid infinite loops with zero-width matches
      if (m.index === dateRegex.lastIndex) {
        dateRegex.lastIndex++;
      }
      _dates.push({title: m[0], hash: itemHash});
    }

    return _dates;
  }
  useEffect(() => {
    if(textTree == null) {
      return
    }
    setDateAnchors(extractDates(textTree));
  }, [textTree]);
  const scrollContentIdIntoView = (contentId) => {
    if (treeLookup[contentId] !== undefined) {
      const ele = document.getElementById(treeLookup[contentId]);
      if (ele) {
        history.location.hash = treeLookup[contentId];
        ele.scrollIntoView();
      }
    }
  }

  return (
    <Card className="page">
      <Button
        className="congress-link"
        icon="share"
        onClick={() => {  window.open(`https://congress.gov/bill/${bill.congress}-congress/${bill.chamber}-bill/${bill.number}`, '_blank') }}
      />
      <h1>{`${chamberLookup[bill.chamber]} ${bill.number}`} - {bill.title}</h1>

      <Divider />
      <div className="sidebar">
        <Tabs id="sidebar-tabs" selectedTabId={selectedTab} onChange={setSelectedTab}>
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
                    onChange={(e) => setBillVers(e.currentTarget.value)}
                    className="bp3"
                    options={lodash.map(
                      bill.legislation_versions,
                      ({ legislation_version, effective_date }, ind) => {
                        return {
                          label: `${legislation_version} ${effective_date !== "None" ? ` - ${effective_date}` : ''}`,
                          value: legislation_version
                        };
                      }
                    )}
                  />
                </FormGroup>

                <FormGroup
                  label="Display Options:"
                >
                  <Switch
                    label="Highlight dates"
                    value={actionParse}
                    onClick={() => setActionParse(!actionParse)}
                  />
                  <Switch
                    label="Highlight spending"
                    value={actionParse}
                    onClick={() => setActionParse(!actionParse)}
                  />
                  <Switch
                    label="Highlight tags"
                    value={actionParse}
                    onClick={() => setActionParse(!actionParse)}
                  />
                  <Switch
                    label="Action parsing details"
                    value={actionParse}
                    onClick={() => setActionParse(!actionParse)}
                  />
                </FormGroup>
              </>
            }
          />
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
          {bill2 && bill2.appropriations && bill2.appropriations.length > 0 && (
            <Tab
              id="dollarlist"
              title="Dollars"
              panel={<AppropriationTree appropriations={bill2.appropriations} onNavigate={scrollContentIdIntoView}/>}
            />
          )}

        </Tabs>
      </div>

      <div className="content">
        <Callout>
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
        </Callout>
      </div>
    </Card>
  );
}

export default BillViewer;
