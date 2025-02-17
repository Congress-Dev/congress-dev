import { BillTable } from "components";
import { getUSCTrackingBills } from "common/api";
import { useEffect, useState } from "react";
export default function USCTrackingTabs({ folderId }) {
    const [bills, setBills] = useState([]);

    useEffect(() => {
        getUSCTrackingBills(folderId)
            .then((res) => res.json())
            .then((res) => {
                setBills(res["legislation"] || []);
            });
    }, [folderId]);
    if (bills.length === 0) {
        return <div>None...</div>;
    }
    return <BillTable bills={bills} />;
}
