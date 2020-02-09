import React, { useEffect, useState } from "react";
import lodash from "lodash";

import { Checkbox } from "@blueprintjs/core";

import { getBillSummary } from "common/api.js";

import BillDisplay from "components/billdisplay";

// Default bill versions to choose
const defaultVers = {
  house: "IH",
  senate: "IS",
};

function BillViewer(props) {
  const [bill, setBill] = useState({});
  const [billVers, setBillVers] = useState("");
  useEffect(() => {
    // Grab the info from the rest API
    const { congress, chamber, billNumber, billVersion } = props.match.params;
    // If we didn't get a bill version, default to the introduced one.
    if (billVersion === undefined) {
      console.log("Setting default");
      setBillVers(defaultVers[chamber.toLowerCase()]);
    } else {
      console.log("Setting", billVersion);
      setBillVers(billVersion);
    }
    getBillSummary(congress, chamber, billNumber).then(setBill);
  }, []);
  useEffect(() => {
    // When the user selects a new version, update the url
    // TODO: Update this to replace state when changing the bill version multiple times
    const { congress, chamber, billNumber } = props.match.params;
    if (billVers !== undefined) {
      props.history.push(`/bill/${congress}/${chamber}/${billNumber}/${billVers}`);
    }
    console.log("Changed bill vers");
  }, [billVers]);
  console.log("Rendering", billVers);
  const { congress, chamber, billNumber, billVersion } = props.match.params;
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
      <Checkbox label="Show Estimated Changes" />
      <hr />
      <BillDisplay
        congress={congress}
        chamber={chamber}
        billNumber={billNumber}
        billVersion={billVers || billVersion}
      />
    </>
  );
}

export default BillViewer;
