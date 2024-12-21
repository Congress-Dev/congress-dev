// Handles searching the API for bills matching the criteria
import React, { useEffect, useState } from "react";
import lodash from "lodash";

import BillCard from "components";
import { getCongressSearch } from "common/api";

function BillSearchContent(props) {
    const [billList, setBillList] = useState({
        legislation: [],
        total_results: 0,
    });

    useEffect(() => {
        getCongressSearch(
            props.congress,
            props.chamber,
            props.versions,
            props.text,
            props.page,
            props.pageSize,
        ).then(setBillList);
    }, [
        props.congress,
        props.chamber,
        props.versions,
        props.text,
        props.page,
        props.pageSize,
    ]);

    useEffect(() => {
        props.setResults(billList.total_results);
    }, [billList.total_results]);

    function renderCardList(billItem, ind) {
        return <BillCard bill={billItem} key={`bill-search-list-${ind}`} />;
    }

    return <>{lodash.map(billList.legislation, renderCardList)}</>;
}

export default BillSearchContent;
