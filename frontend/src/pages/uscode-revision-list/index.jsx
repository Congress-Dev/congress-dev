import React, { useEffect, useState } from "react";
import lodash from "lodash";
import {
    Section,
    SectionCard,
    InputGroup,
    Button,
    Collapse,
    Icon,
} from "@blueprintjs/core";

import { USCRevisionBox, USCView } from "components";
import { getUSCRevisions, getUSCodeSearch } from "common/api";

import { getUSCSectionContent } from "common/api";
import { md5 } from "common/other";
function USCodeRevisionList() {
    const [releases, setReleases] = useState([]);
    const [query, setQuery] = useState("");
    const [searchResults, setSearchResults] = useState([]);
    const [expandedResults, setExpandedResults] = useState({});
    useEffect(() => {
        getUSCRevisions().then(setReleases);
    }, []);

    const executeSearch = () => {
        if (!query.trim()) return;
        getUSCodeSearch(query).then((results) => {
            setSearchResults(results);
        });
    };
    const toggleExpand = (index) => {
        setExpandedResults((prev) => ({
            ...prev,
            [index]: !prev[index],
        }));
    };

    const renderSearchResults = () => {
        if (!searchResults || searchResults.length === 0) return null;
        return searchResults.map((result, index) => {
            const isExpanded = !!expandedResults[index];

            return (
                <SectionCard
                    key={`search-result-${index}`}
                    className="search-result"
                >
                    <div
                        className="result-header"
                        onClick={() => toggleExpand(index)}
                        style={{
                            cursor: "pointer",
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                        }}
                    >
                        <div>
                            <strong>
                                Ch. {result.usc_link.split("/")[0]} -{" "}
                                {result.title} | S.{" "}
                                {result.usc_link.split("/")[1]} -{" "}
                                {result.section_display}
                            </strong>
                        </div>
                        <Icon
                            icon={isExpanded ? "chevron-up" : "chevron-down"}
                        />
                    </div>

                    <Collapse isOpen={isExpanded}>
                        <div
                            className="result-content"
                            style={{ marginTop: "10px" }}
                        >
                            <USCView
                                release={"latest"}
                                section={result.usc_link.split("/")[1]}
                                title={result.usc_link.split("/")[0]}
                            />
                        </div>
                    </Collapse>

                    {!isExpanded && (
                        <div
                            className="text-preview"
                            style={{
                                marginTop: "5px",
                                color: "#666",
                                maxHeight: "3em", // Set a maximum height (approximately 2-3 lines)
                                overflow: "hidden",
                                textOverflow: "ellipsis",
                                display: "-webkit-box",
                                WebkitLineClamp: 2, // Number of lines to show
                                WebkitBoxOrient: "vertical",
                            }}
                        >
                            {console.log("hidden")}
                            <USCView
                                release={"latest"}
                                section={result.usc_link.split("/")[1]}
                                title={result.usc_link.split("/")[0]}
                                lines={3}
                            />
                        </div>
                    )}
                </SectionCard>
            );
        });
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
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                executeSearch();
                            }
                        }}
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
