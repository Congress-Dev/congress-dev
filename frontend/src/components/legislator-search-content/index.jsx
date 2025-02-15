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
import { getMemberSearch } from "common/api";

function LegislatorSearchContent(props) {
    const [memberList, setMemberList] = useState({
        members: [],
        total_results: 0,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getMemberSearch(
          props.name,
          undefined,
          undefined,
          props.chamber?.split(","),
          props.sort,
          props.direction,
          props.page,
          props.pageSize,
        ).then((billList) => {
            if (billList != null) {
                setLoading(false);
                setMemberList(billList);
            }
        });
    }, [
        props.name,
        props.page,
        props.pageSize,
        props.sort,
        props.direction,
    ]);

    useEffect(() => {
        props.setResults(memberList.total_results);
    }, [props.setResults, memberList.total_results]);

    function renderCardList(memberItem, ind) {
        return (
            <LegislatorCard
                legislator={memberItem}
                key={`member-search-list-${ind}`}
            />
        );
    }

    return loading ? (
        <Spinner className="loading-spinner" intent="primary" />
    ) : (
        <>
            {memberList.members.length > 0 ? (
                lodash.map(memberList.members, renderCardList)
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
