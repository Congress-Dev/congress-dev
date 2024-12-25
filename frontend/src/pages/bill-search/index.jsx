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
    ButtonGroup,
} from "@blueprintjs/core";
import qs from "query-string";

import { initialVersionToFull, versionToFull } from "common/lookups";
import { BillSearchContent, CollapsibleSection, Paginator } from "components";

function BillSearch(props) {
    const location = useLocation();
    const [isFirstRender, setFirstRender] = useState(true);
    const [resPageSize, setResPageSize] = useState(5);
    const [chamberButtons, setChamberButtons] = useState({
        House: true,
        Senate: true,
    });
    const [versionButtons, setVersionButtons] = useState(initialVersionToFull);
    const [textBox, setTextBox] = useState("");
    const [sortField, setSortField] = useState("number");
    const [totalResults, setTotalResults] = useState(0);

    const searchParams = new URLSearchParams(location.search);
    const [currentSearch, setCurrentSearch] = useState({
        congress: "118",
        chamber: "House,Senate",
        versions: Object.keys(versionToFull).join(","),
        text: "",
        sort: "number",
        page:  searchParams.get('page') || 1,
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
        const versionKeys = lodash.keys(
            lodash.pickBy(versionButtons, (value) => value),
        );

        setCurrentSearch({
            ...currentSearch,
            page: 1,
            chamber: lodash
                .keys(lodash.pickBy(chamberButtons, (value) => value))
                .join(","),
            versions: lodash
                .keys(
                    lodash.pickBy(versionToFull, (value) =>
                        versionKeys.includes(value),
                    ),
                )
                .join(","),
            text: textBox,
            sort: sortField,
        });
        setCurrentPage(1);
    }

    useEffect(() => {
        const params = qs.parse(props.location.search);
        if(currentSearch.page != params.page) {
            setCurrentSearch({
                ...currentSearch,
                page: params.page,
            });
        }
      }, [props.location.search]);

    useEffect(() => {
        const urlSearchParams = new URLSearchParams(location.search);
        urlSearchParams.set('page', currentSearch.page);
        props.history.push({
            pathname: props.location.pathname,
            search: urlSearchParams.toString(),
        });
    }, [currentSearch])

    function setCurrentPage(page) {
        setCurrentSearch({
            ...currentSearch,
            page: page,
        });
    }

    useEffect(() => {
        if(isFirstRender) {
            setFirstRender(false);
            return
        }
        executeSearch();
    }, [versionButtons, chamberButtons, sortField]);

    return (
        <Card className="page" elevation={Elevation.ONE}>
            <div className="sidebar">
                <FormGroup labelFor="text-input">
                    <ControlGroup fill={true}>
                        <HTMLSelect
                            options={[
                                { label: "Bill No.", value: "number" },
                                { label: "Title", value: "title" },
                                { label: "Date", value: "effective_date" },
                            ]}
                            onChange={(event) => {
                                setSortField(event.currentTarget.value);
                            }}
                        />
                        <InputGroup
                            value={textBox}
                            onChange={(event) => {
                                setTextBox(event.target.value);
                            }}
                            rightElement={
                                <Button
                                    icon="arrow-right"
                                    intent="primary"
                                    onClick={executeSearch}
                                />
                            }
                        />
                    </ControlGroup>
                </FormGroup>
                <Divider />
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
                    <Button icon="remove" onClick={toggleUncheckAll}></Button>
                    <Button icon="th-filtered" onClick={toggleEnrolled}>
                        Enrolled
                    </Button>
                </ButtonGroup>
                <CollapsibleSection
                    title="Session of Congress"
                    collapsed={collapsed}
                ></CollapsibleSection>
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
            <div className="content">
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
                <div className="search-count">
                    Total Results: {totalResults}
                </div>
                <Paginator
                    currentPage={parseInt(currentSearch.page)}
                    totalPages={Math.ceil(totalResults / currentSearch.pageSize)}
                    onPage={(page) => {
                        setCurrentPage(page);
                    }}
                />
            </div>
        </Card>
    );
}

export default BillSearch;
