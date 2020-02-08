import React, { useEffect, useState } from 'react';
import lodash from 'lodash';
import { endpoint } from 'common/api.js';

function capFirstLetter(str) {
    return str.charAt(0).toUpperCase() + str.substring(1);
}
function BillViewer(props) {
    const [bill, setBill] = useState({});
    const [billVers, setBillVers] = useState("");
    useEffect(() => {
        // Grab the info from the rest API
        const { congress, chamber, billNumber, billVersion } = props.match.params;
        setBillVers(billVersion);
        fetch(`${endpoint}/congress/${congress}/${capFirstLetter(chamber)}-bill/${billNumber}`)
            .then((res) => res.json())
            .then(setBill);
    }, []);
    useEffect(() => {
        // When the user selects a new version, update the url
        // TODO: Update this to replace state when changing the bill version multiple times
        const { congress, chamber, billNumber } = props.match.params;
        if (billVers !== undefined) {
            props.history.push(`/bill/${congress}/${chamber}/${billNumber}/${billVers}`);
        }
    }, [billVers]);

    return (<>
        <h3>
            {bill.title}
        </h3>Selected Version:{" "}
        <select
            id="bill-version-select"
            value={(billVers || "").toUpperCase()}
            onChange={(e) => setBillVers(e.target.value)}>
            {
                lodash.map(bill.legislation_versions, ({ legislation_version, effective_date }, ind) => {
                    return <option value={legislation_version} key={`bill-version-select-${ind}`}>
                        {legislation_version}{effective_date !== "None" ? ` - ${effective_date}` : null}</option>
                })
            }
        </select></>);
}

export default BillViewer;