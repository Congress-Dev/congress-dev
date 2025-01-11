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
    SectionCard,
    ControlGroup,
    HTMLSelect,
    RadioGroup,
    Radio,
    ButtonGroup,
    Section,
    Icon,
} from "@blueprintjs/core";
import qs from "query-string";

import { initialVersionToFull, versionToFull } from "common/lookups";
import { BillSearchContent, CollapsibleSection, Paginator } from "components";

function BillSearch(props) {
    const location = useLocation();
    const searchParams = new URLSearchParams(location.search);

    const decoded = decodeSelections(searchParams.get("selections"));

    const [isFirstRender, setFirstRender] = useState(true);
    const [resPageSize, setResPageSize] = useState(5);
    const [chamberButtons, setChamberButtons] = useState(decoded.chamber);
    const [versionButtons, setVersionButtons] = useState(decoded.versions);
    const [textBox, setTextBox] = useState(searchParams.get("text") || "");
    const [totalResults, setTotalResults] = useState(0);
    const [currentCongress, setCurrentCongress] = useState("119");

    const [currentSearch, setCurrentSearch] = useState({
        congress: currentCongress,
        chamber: lodash
            .keys(lodash.pickBy(chamberButtons, (value) => value))
            .join(","),
        versions: lodash
            .keys(
                lodash.pickBy(versionToFull, (value) =>
                    lodash
                        .keys(lodash.pickBy(versionButtons, (value) => value))
                        .includes(value),
                ),
            )
            .join(","),
        text: searchParams.get("text") || "",
        sort: searchParams.get("sort") || "number",
        page: searchParams.get("page") || 1,
        pageSize: resPageSize,
    });

    const [collapsed, setCollapsed] = useState(false); // State to control the signal

    function toggleCollapseAll() {
        setCollapsed(true);
    }

    function toggleExpandAll() {
        setCollapsed(false);
    }

    function toggleEnrolled() {
        setVersionButtons({
            ...lodash.mapValues(initialVersionToFull, () => {
                return false;
            }),
            Enrolled: true,
        });
    }

    function toggleCheckAll() {
        setChamberButtons({ House: true, Senate: true });
        setVersionButtons(
            lodash.mapValues(initialVersionToFull, () => {
                return true;
            }),
        );
    }

    function toggleUncheckAll() {
        setChamberButtons({ House: false, Senate: false });
        setVersionButtons(
            lodash.mapValues(initialVersionToFull, () => {
                return false;
            }),
        );
    }

    function executeSearch() {
        setCurrentSearch({
            ...currentSearch,
            page: 1,
            congress: currentCongress,
            chamber: lodash
                .keys(lodash.pickBy(chamberButtons, (value) => value))
                .join(","),
            versions: lodash
                .keys(
                    lodash.pickBy(versionToFull, (value) =>
                        lodash
                            .keys(
                                lodash.pickBy(versionButtons, (value) => value),
                            )
                            .includes(value),
                    ),
                )
                .join(","),
            text: textBox,
        });
    }

    function encodeSelections() {
        let encoded = "1";
        lodash.mapValues(chamberButtons, (v, k) => {
            encoded += v ? "1" : "0";
        });
        lodash.mapValues(versionButtons, (v, k) => {
            encoded += v ? "1" : "0";
        });
        return parseInt(encoded, 2);
    }

    function decodeSelections(selections) {
        if (selections == null || selections == "") {
            return {
                chamber: {
                    House: true,
                    Senate: true,
                },
                versions: initialVersionToFull,
            };
        }

        let bits = Number(selections).toString(2).split("");
        let index = 1;

        const chamber = lodash.mapValues(
            { House: true, Senate: true },
            (v, k) => {
                const value = bits[index] == "1" ? true : false;
                index++;
                return value;
            },
        );
        const versions = lodash.mapValues(initialVersionToFull, (v, k) => {
            const value = bits[index] == "1" ? true : false;
            index++;
            return value;
        });

        return {
            chamber,
            versions,
        };
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
        if (params.text != null && currentSearch.text != params.text) {
            updated = true;
            newSearch = {
                ...newSearch,
                text: params.text,
            };
        }

        const encoded = encodeSelections();
        if (params.selection != null && encoded != params.selection) {
            updated = true;

            const decoded = decodeSelections(params.selection);
            newSearch = {
                ...newSearch,
                chamber: decoded.chamber,
                versions: decoded.versions,
            };
        }

        if (updated) {
            setCurrentSearch(newSearch);
        }
    }, [props.location.search]);

    useEffect(() => {
        let updated = false;
        const params = qs.parse(props.location.search);
        if (currentSearch.page != null && params.page != currentSearch.page) {
            updated = true;
            params.page = currentSearch.page;
        }
        if (currentSearch.sort != null && params.sort != currentSearch.sort) {
            updated = true;
            params.sort = currentSearch.sort;
        }
        if (currentSearch.text == "" && params.text != null) {
            updated = true;
            delete params.text;
        } else if (
            currentSearch.text != "" &&
            params.text != currentSearch.text
        ) {
            updated = true;
            params.text = currentSearch.text;
        }

        const encoded = encodeSelections();
        if (encoded != null && params.selections != encoded) {
            updated = true;
            params.selections = encoded;
        }

        if (updated) {
            props.history.push({
                pathname: props.location.pathname,
                search: qs.stringify(params, { encode: false }),
            });
        }
    }, [currentSearch]);

    function setCurrentPage(page) {
        setCurrentSearch({
            ...currentSearch,
            page: page,
        });
    }

    useEffect(() => {
        if (isFirstRender) {
            setFirstRender(false);
            return;
        }
        executeSearch();
    }, [versionButtons, chamberButtons, currentCongress]);

    function setCurrentSort(sort) {
        setCurrentSearch({
            ...currentSearch,
            page: 1,
            sort: sort,
        });
    }

    function handleCongressChange(e) {
        setCurrentCongress(e.target.value);
    }

    return (
        <Section
            className="page"
            elevation={Elevation.ONE}
            title="Legislation Search"
            subtitle="Search for legislation by keyword, sponsor, or topic"
        >
            <SectionCard>
                <div className="sidebar">
                    <form
                        onSubmit={(e) => {
                            e.preventDefault();
                            executeSearch();
                        }}
                    >
                        <FormGroup
                            labelFor="text-input"
                            className="search-sort"
                        >
                            <ControlGroup fill={true}>
                                <InputGroup
                                    value={textBox}
                                    leftIcon="search"
                                    onChange={(event) => {
                                        setTextBox(event.target.value);
                                    }}
                                    placeholder="Search"
                                    rightElement={
                                        <Button
                                            type="submit"
                                            icon="arrow-right"
                                            intent="primary"
                                            onClick={executeSearch}
                                        />
                                    }
                                />
                            </ControlGroup>
                        </FormGroup>
                    </form>
                    <ButtonGroup className="collapse-controls" fill={true}>
                        <Button
                            icon="collapse-all"
                            onClick={toggleCollapseAll}
                        ></Button>
                        <Button
                            icon="expand-all"
                            onClick={toggleExpandAll}
                        ></Button>
                        <Button icon="add" onClick={toggleCheckAll}></Button>
                        <Button
                            icon="remove"
                            onClick={toggleUncheckAll}
                        ></Button>
                        <Button
                            className="enrolled-button"
                            icon="th-filtered"
                            onClick={toggleEnrolled}
                        >
                            Enrolled
                        </Button>
                    </ButtonGroup>
                    <CollapsibleSection
                        title="Session of Congress"
                        collapsed={collapsed}
                    >
                        <RadioGroup
                            onChange={handleCongressChange}
                            selectedValue={currentCongress}
                        >
                            <Radio label="119th" value="119" />
                            <Radio label="118th" value="118" />
                        </RadioGroup>
                    </CollapsibleSection>
                    <CollapsibleSection
                        title="Chamber of Origin"
                        collapsed={collapsed}
                    >
                        <Checkbox
                            checked={chamberButtons.House === true}
                            label="House"
                            onChange={() => {
                                setChamberButtons({
                                    ...chamberButtons,
                                    House: !chamberButtons.House,
                                });
                            }}
                        />
                        <Checkbox
                            checked={chamberButtons.Senate === true}
                            label="Senate"
                            onChange={() => {
                                setChamberButtons({
                                    ...chamberButtons,
                                    Senate: !chamberButtons.Senate,
                                });
                            }}
                        />
                    </CollapsibleSection>
                    <CollapsibleSection
                        title="Legislation Status"
                        collapsed={collapsed}
                    >
                        {lodash.map(initialVersionToFull, (value, key) => {
                            return (
                                <Checkbox
                                    key={`checkbox-${key}`}
                                    checked={versionButtons[key] === true}
                                    label={key}
                                    onChange={() => {
                                        setVersionButtons({
                                            ...versionButtons,
                                            [key]: !versionButtons[key],
                                        });
                                    }}
                                />
                            );
                        })}
                    </CollapsibleSection>
                </div>
                <Section
                    title="Results"
                    subtitle={`${totalResults.toLocaleString()} Bills`}
                    className="content"
                    icon="inbox-search"
                    rightElement={
                        <>
                            <Icon icon="sort-alphabetical" /> Sort:
                            <HTMLSelect
                                value={currentSearch.sort}
                                options={[
                                    { label: "Bill No.", value: "number" },
                                    { label: "Title", value: "title" },
                                    { label: "Date", value: "effective_date" },
                                ]}
                                onChange={(event) => {
                                    setCurrentSort(event.currentTarget.value);
                                }}
                            />
                        </>
                    }
                >
                    <BillSearchContent
                        congress={currentSearch.congress}
                        chamber={currentSearch.chamber}
                        versions={currentSearch.versions}
                        text={currentSearch.text}
                        sort={currentSearch.sort}
                        page={currentSearch.page}
                        pageSize={currentSearch.pageSize}
                        setResults={setTotalResults}
                    />
                    {totalResults > 0 ? (
                        <Paginator
                            currentPage={parseInt(currentSearch.page)}
                            totalPages={Math.ceil(
                                totalResults / currentSearch.pageSize,
                            )}
                            onPage={(page) => {
                                setCurrentPage(page);
                            }}
                        />
                    ) : (
                        ""
                    )}
                </Section>
            </SectionCard>
        </Section>
    );
}

export default BillSearch;
