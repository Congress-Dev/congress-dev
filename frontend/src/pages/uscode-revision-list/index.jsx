import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { Section, SectionCard, InputGroup, Button } from "@blueprintjs/core";

import { USCRevisionBox } from "components";
import { getUSCRevisions, getUSCodeSearch } from "common/api";

function USCodeRevisionList() {
    const [releases, setReleases] = useState([]);
    const [query, setQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);

    useEffect(() => {
        getUSCRevisions().then(setReleases);
    }, []);

    const executeSearch = () => {
        if (!query.trim()) return;
        getUSCodeSearch(query).then((results) => {
            setSearchResults(results);
        });
    };

    const renderSearchResults = () => {
        if (!searchResults || searchResults.length === 0) return null;
        return searchResults.map((result, index) => (
            <SectionCard
                key={`search-result-${index}`}
                className="search-result"
            >
                <h3>{result.title}</h3>
                <h4>{result.sectionHeader}</h4>
            </SectionCard>
        ));
    };

    return (
        <>
            <Section
                className="page"
                title="United States Code"
                subtitle="The Foundation of U.S. Law"
            >
                <Section
                    className="full"
                    title="Release Points"
                    subtitle="Different versions of the USCode, typically aligned around the passage of major legislation"
                    icon="pin"
                    collapsible={true}
                >
                    {lodash.map(
                        releases,
                        (
                            {
                                usc_release_id,
                                effective_date,
                                long_title,
                                short_title,
                                url,
                            },
                            ind,
                        ) => (
                            <USCRevisionBox
                                key={`usc-rev-box-${ind}`}
                                usc_release_id={usc_release_id}
                                effective_date={effective_date}
                                long_title={long_title}
                                short_title={short_title}
                                url={
                                    "https://uscode.house.gov/download/releasepoints/us/pl/116/78/usc-rp@116-78.htm"
                                }
                            />
                        ),
                    )}
                </Section>
                <Section
                    className="full"
                    title="Intelligent Search"
                    subtitle="Search the USCode for sections pertaining to a specific topic using natural language"
                    icon="search-text"
                    collapsible={true}
                >
                    <InputGroup
                        placeholder="Enter search text..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        rightElement={
                            <Button icon="search" onClick={executeSearch} />
                        }
                    />
                    <div className="search-results">
                        {renderSearchResults()}
                    </div>
                </Section>
            </Section>
        </>
    );
}

export default USCodeRevisionList;
