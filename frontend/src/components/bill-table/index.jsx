import { Link } from "react-router-dom";
import { HTMLTable } from "@blueprintjs/core";

import { chamberLookup } from "common/lookups";
import { LegislatorChip } from "components";

function BillTable({ bills }) {
    return (
        <HTMLTable compact={true} striped={true} className="section-bill-table">
            <thead>
                <tr>
                    <th className="fixed critical">No.</th>
                    {"effective_date" in bills[0] && (
                        <th className="fixed">Effective Date</th>
                    )}
                    <th className="critical">Name</th>
                    {"sponsor" in bills[0] && (
                        <th className="fixed">Sponsor</th>
                    )}
                </tr>
            </thead>

            <tbody>
                {bills.map((bill, idx) => (
                    <tr key={idx}>
                        <td className="fixed critical">
                            <Link
                                to={`/bill/${bill.congress || bill.session_number}/${bill.chamber}/${bill.number}`}
                            >
                                {`${chamberLookup[bill.chamber]} ${bill.number}`}
                            </Link>
                        </td>
                        {"effective_date" in bills[0] && (
                            <td className="fixed">{bill.effective_date}</td>
                        )}
                        <td className="critical">{bill.title}</td>
                        {"sponsor" in bills[0] && (
                            <td className="fixed">
                                <LegislatorChip sponsor={bill.sponsor} />
                            </td>
                        )}
                    </tr>
                ))}
            </tbody>
        </HTMLTable>
    );
}

export default BillTable;
