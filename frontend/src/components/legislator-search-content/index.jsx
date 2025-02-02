// Handles searching the API for bills matching the criteria
import React, { useEffect, useState } from "react";
import lodash from "lodash";
import {
    SectionCard,
    Spinner,
    NonIdealState,
    NonIdealStateIconSize,
} from "@blueprintjs/core";

import { LegislatorCard } from "components";
import { getCongressSearch } from "common/api";

function LegislatorSearchContent(props) {
    const [memberList, setMemberList] = useState({
        members: [],
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
                setMemberList(billList);
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
        props.setResults(memberList.total_results);
    }, [memberList.total_results]);

    function renderCardList(memberItem, ind) {
        return (
            <LegislatorCard
                bill={memberItem}
                key={`member-search-list-${ind}`}
            />
        );
    }

    return loading ? (
        <Spinner className="loading-spinner" intent="primary" />
    ) : (
        <>
            {memberList.legislation.length > 0 ? (
                lodash.map(memberList.legislation, renderCardList)
            ) : (
                <SectionCard className="member-card">
                    <NonIdealState
                        icon="search"
                        iconSize={NonIdealStateIconSize.STANDARD}
                        title="No search results"
                        description={
                            <>
                                Your search didn't match any members.
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

export default LegislatorSearchContent;
