import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import lodash from "lodash";
import {
    Card,
    Elevation,
    FormGroup,
    InputGroup,
    Checkbox,
    Button,
    Divider,
    ControlGroup,
    HTMLSelect,
    RadioGroup,
    Radio,
    ButtonGroup,
    Section,
    Icon,
    Spinner,
    NonIdealState,
} from "@blueprintjs/core";
import qs from "query-string";

import { getCommittees } from "common/api";
import { CollapsibleSection, Paginator } from "components";
import CommitteeCard from "components/committee-card";
import "./styles.scss";

function CommitteeSearch(props) {
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);

    const [isFirstRender, setFirstRender] = useState(true);
    const [resPageSize, setResPageSize] = useState(10);
    const [chamberButtons, setChamberButtons] = useState({
        House: true,
        Senate: true,
    });
    const [textBox, setTextBox] = useState(searchParams.get("name") || "");
    const [totalResults, setTotalResults] = useState(0);
    const [committees, setCommittees] = useState([]);
    const [loading, setLoading] = useState(false);
    const [congressFilter, setCongressFilter] = useState(
        searchParams.get("congress") || "118,119"
    );
    const [committeeTypeFilter, setCommitteeTypeFilter] = useState(
        searchParams.get("committee_type") || ""
    );

    const [currentSearch, setCurrentSearch] = useState({
        congress: searchParams.get("congress") || "118,119",
        chamber: lodash
            .keys(lodash.pickBy(chamberButtons, (value) => value))
            .filter(Boolean),
        name: searchParams.get("name") || "",
        committee_type: searchParams.get("committee_type") || "",
        sort: searchParams.get("sort") || "name",
        direction: searchParams.get("direction") || "asc",
        page: searchParams.get("page") || 1,
        pageSize: resPageSize,
    });

    const [collapsed, setCollapsed] = useState(false);

    function toggleCollapseAll() {
        setCollapsed(true);
    }

    function toggleExpandAll() {
        setCollapsed(false);
    }

    function toggleCheckAll() {
        setChamberButtons({ House: true, Senate: true });
    }

    function toggleUncheckAll() {
        setChamberButtons({ House: false, Senate: false });
    }

    function executeSearch() {
        setCurrentSearch({
            ...currentSearch,
            page: 1,
            chamber: lodash
                .keys(lodash.pickBy(chamberButtons, (value) => value))
                .filter(Boolean),
            name: textBox,
            congress: congressFilter.split(',').filter(Boolean),
            committee_type: committeeTypeFilter,
        });
    }

    useEffect(() => {
        let updated = false;
        const params = qs.parse(props.location.search);
        let newSearch = {
            ...currentSearch,
        };
        if (params.page != null && currentSearch.page != params.page) {
            updated = true;
            newSearch = {
                ...newSearch,
                page: params.page,
            };
        }
        if (params.sort != null && currentSearch.sort != params.sort) {
            updated = true;
            newSearch = {
                ...newSearch,
                sort: params.sort,
            };
        }
        if (
            params.direction != null &&
            currentSearch.direction != params.direction
        ) {
            updated = true;
            newSearch = {
                ...newSearch,
                direction: params.direction,
            };
        }
        if (updated) {
            setCurrentSearch(newSearch);
        }
    }, [props.location.search]);

    useEffect(() => {
        if (isFirstRender) {
            setFirstRender(false);
            return;
        }

        setLoading(true);
        getCommittees(
            currentSearch.name,
            currentSearch.chamber,
            currentSearch.congress,
            currentSearch.committee_type,
            currentSearch.sort,
            currentSearch.direction,
            currentSearch.page,
            currentSearch.pageSize
        )
            .then((response) => {
                if (response) {
                    setCommittees(response.committees || []);
                    setTotalResults(response.total_results || 0);
                }
            })
            .catch((error) => {
                console.error("Error fetching committees:", error);
                setCommittees([]);
                setTotalResults(0);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [currentSearch]);

    function setCurrentPage(page) {
        const params = qs.parse(props.location.search);
        params.page = page;
        props.history.push({
            pathname: props.location.pathname,
            search: qs.stringify(params),
        });
    }

    function setCurrentSort(sort) {
        const params = qs.parse(props.location.search);
        params.sort = sort;
        delete params.page;
        props.history.push({
            pathname: props.location.pathname,
            search: qs.stringify(params),
        });
    }

    function setCurrentDirection(direction) {
        const params = qs.parse(props.location.search);
        params.direction = direction;
        delete params.page;
        props.history.push({
            pathname: props.location.pathname,
            search: qs.stringify(params),
        });
    }

    const congressOptions = [
        { value: "118,119", label: "118th & 119th Congress" },
        { value: "119", label: "119th Congress" },
        { value: "118", label: "118th Congress" },
        { value: "117", label: "117th Congress" },
        { value: "116", label: "116th Congress" },
    ];

    const typeOptions = [
        { value: "", label: "All Types" },
        { value: "Standing", label: "Standing" },
        { value: "Joint", label: "Joint" },
        { value: "Select", label: "Select" },
        { value: "Special", label: "Special" },
    ];

    return (
        <div className="committee-search-page">
            <div className="search-container">
                <Card elevation={Elevation.TWO} className="search-card">
                    <div className="search-header">
                        <h2>Committee Search</h2>
                        <div className="collapse-controls">
                            <Button
                                minimal
                                small
                                onClick={toggleExpandAll}
                                icon="expand-all"
                            >
                                Expand All
                            </Button>
                            <Button
                                minimal
                                small
                                onClick={toggleCollapseAll}
                                icon="collapse-all"
                            >
                                Collapse All
                            </Button>
                        </div>
                    </div>

                    <div className="search-form">
                        <FormGroup
                            label="Committee Name"
                            labelFor="committee-name-input"
                        >
                            <InputGroup
                                id="committee-name-input"
                                placeholder="Search by committee name..."
                                value={textBox}
                                onChange={(e) => setTextBox(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === "Enter") {
                                        executeSearch();
                                    }
                                }}
                            />
                        </FormGroup>

                        <CollapsibleSection
                            title="Congress"
                            collapsed={collapsed}
                        >
                            <HTMLSelect
                                value={congressFilter}
                                onChange={(e) => setCongressFilter(e.target.value)}
                                options={congressOptions}
                                fill
                            />
                        </CollapsibleSection>

                        <CollapsibleSection
                            title="Committee Type"
                            collapsed={collapsed}
                        >
                            <HTMLSelect
                                value={committeeTypeFilter}
                                onChange={(e) => setCommitteeTypeFilter(e.target.value)}
                                options={typeOptions}
                                fill
                            />
                        </CollapsibleSection>

                        <CollapsibleSection title="Chamber" collapsed={collapsed}>
                            <div className="chamber-controls">
                                <ButtonGroup minimal>
                                    <Button
                                        small
                                        onClick={toggleCheckAll}
                                        icon="tick"
                                    >
                                        Check All
                                    </Button>
                                    <Button
                                        small
                                        onClick={toggleUncheckAll}
                                        icon="cross"
                                    >
                                        Uncheck All
                                    </Button>
                                </ButtonGroup>
                            </div>
                            <div className="checkbox-group">
                                <Checkbox
                                    checked={chamberButtons.House}
                                    label="House"
                                    onChange={(e) =>
                                        setChamberButtons({
                                            ...chamberButtons,
                                            House: e.target.checked,
                                        })
                                    }
                                />
                                <Checkbox
                                    checked={chamberButtons.Senate}
                                    label="Senate"
                                    onChange={(e) =>
                                        setChamberButtons({
                                            ...chamberButtons,
                                            Senate: e.target.checked,
                                        })
                                    }
                                />
                            </div>
                        </CollapsibleSection>

                        <div className="search-actions">
                            <Button
                                intent="primary"
                                onClick={executeSearch}
                                loading={loading}
                                icon="search"
                            >
                                Search Committees
                            </Button>
                        </div>
                    </div>
                </Card>

                <div className="results-section">
                    <div className="results-header">
                        <div className="results-info">
                            {totalResults > 0 && (
                                <p>
                                    Found {totalResults} committee
                                    {totalResults !== 1 ? "s" : ""}
                                </p>
                            )}
                        </div>
                        <div className="sort-controls">
                            <HTMLSelect
                                value={currentSearch.sort}
                                onChange={(e) => setCurrentSort(e.target.value)}
                                options={[
                                    { value: "name", label: "Name" },
                                    { value: "congress_id", label: "Congress" },
                                    { value: "chamber", label: "Chamber" },
                                    { value: "committee_type", label: "Type" },
                                ]}
                            />
                            <ButtonGroup>
                                <Button
                                    active={currentSearch.direction === "asc"}
                                    onClick={() => setCurrentDirection("asc")}
                                    icon="sort-asc"
                                    small
                                />
                                <Button
                                    active={currentSearch.direction === "desc"}
                                    onClick={() => setCurrentDirection("desc")}
                                    icon="sort-desc"
                                    small
                                />
                            </ButtonGroup>
                        </div>
                    </div>

                    {loading ? (
                        <div className="loading-container">
                            <Spinner size={50} />
                            <p>Loading committees...</p>
                        </div>
                    ) : committees.length > 0 ? (
                        <>
                            <div className="committee-list">
                                {committees.map((committee) => (
                                    <CommitteeCard
                                        key={committee.legislation_committee_id}
                                        committee={committee}
                                    />
                                ))}
                            </div>
                            <Paginator
                                currentPage={parseInt(currentSearch.page)}
                                totalResults={totalResults}
                                pageSize={currentSearch.pageSize}
                                setCurrentPage={setCurrentPage}
                            />
                        </>
                    ) : (
                        <NonIdealState
                            icon="search"
                            title="No committees found"
                            description="Try adjusting your search criteria or filters."
                        />
                    )}
                </div>
            </div>
        </div>
    );
}

export default CommitteeSearch; 