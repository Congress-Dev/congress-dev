import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { Checkbox } from "@blueprintjs/core";

import { getBillSummary, getBillVersionDiffForSection } from "common/api.js";

import BillDisplay from "components/billdisplay";
import BillDiffSidebar from "components/billdiffsidebar";
import USCView from "components/uscview";

// Default bill versions to choose
const defaultVers = {
  house: "IH",
  senate: "IS",
};

function BillViewer(props) {
  // TODO: Add sidebar for viewing the differences that a bill will generate
  // TODO: Option for comparing two versions of the same bill and highlighting differences
  const [bill, setBill] = useState({});
  const [diffs, setDiffs] = useState({});
  const [actionParse, setActionParse] = useState(false);

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
      props.history.push(
        `/bill/${congress}/${chamber}/${billNumber}/${billVers ||
          billVersion}${diffStr}`
      );
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
  return (
    <>
      <h3>{bill.title}</h3>Selected Version:{" "}
      <select
        id="bill-version-select"
        value={(billVers || "").toUpperCase()}
        onChange={e => setBillVers(e.target.value)}
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
      <div className="sidebar">
        <BillDiffSidebar
          congress={congress}
          chamber={chamber}
          billNumber={billNumber}
          billVersion={billVers || billVersion}
        />
      </div>
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
            showTooltips={actionParse}
          />
        )}
      </div>
    </>
  );
}

export default BillViewer;
