// Handles searching the API for bills matching the criteria
import React, { useEffect, useState } from "react";
import lodash from "lodash";
import {
    SectionCard,
    Spinner,
    NonIdealState,
    NonIdealStateIconSize,
} from "@blueprintjs/core";

import { BillCard } from "components";
import { getCongressSearch } from "common/api";

function BillSearchContent(props) {
    const [billList, setBillList] = useState({
        legislation: [],
        total_results: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getCongressSearch(
            props.congress,
            props.chamber,
            props.versions,
            props.text,
            props.sort,
            props.page,
            props.pageSize,
        ).then((billList) => {
            if (billList != null) {
                setLoading(false);
                setBillList(billList);
            }
        });
    }, [
        props.congress,
        props.chamber,
        props.versions,
        props.text,
        props.sort,
        props.page,
        props.pageSize,
    ]);

    useEffect(() => {
        props.setResults(billList.total_results);
    }, [billList.total_results]);

    function renderCardList(billItem, ind) {
        return <BillCard bill={billItem} key={`bill-search-list-${ind}`} />;
    }

    return loading ? (
        <Spinner className="loading-spinner" intent="primary" />
    ) : (
        <>
            {billList.legislation.length > 0 ? (
                lodash.map(billList.legislation, renderCardList)
            ) : (
                <SectionCard className="bill-card">
                    <NonIdealState
                        icon="search"
                        iconSize={NonIdealStateIconSize.STANDARD}
                        title="No search results"
                        description={
                            <>
                                Your search didn't match any bills.
                                <br />
                                Try searching for something else, or select more
                                filters.
                            </>
                        }
                        layout="vertical"
                    />
                </SectionCard>
            )}
        </>
    );
}

export default BillSearchContent;
