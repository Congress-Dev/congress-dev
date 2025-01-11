import { Link } from "react-router-dom";
import { HTMLTable } from "@blueprintjs/core";

import { chamberLookup } from "common/lookups";
import { LegislatorChip } from "components";

function BillTable({ bills }) {
    return (
        <HTMLTable compact={true} striped={true} className="section-bill-table">
            <thead>
                <tr>
                    <th>No.</th>
                    <th>Effective Date</th>
                    <th>Name</th>
                    <th>Sponsor</th>
                </tr>
            </thead>

            <tbody>
                {bills.map((bill, idx) => (
                    <tr key={idx}>
                        <td>
                            <Link
                                to={`/bill/${bill.congress || bill.session_number}/${bill.chamber}/${bill.number}`}
                            >
                                {`${chamberLookup[bill.chamber]} ${bill.number}`}
                            </Link>
                        </td>
                        <td>{bill.effective_date}</td>
                        <td>{bill.title}</td>
                        <td>
                            <LegislatorChip sponsor={bill.sponsor} />
                        </td>
                    </tr>
                ))}
            </tbody>
        </HTMLTable>
    );
}

export default BillTable;
