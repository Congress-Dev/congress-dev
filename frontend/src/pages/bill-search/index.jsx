import React, { useState, useEffect } from "react";
import lodash from "lodash";
import qs from "query-string";
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

import { initialVersionToFull, versionToFull } from "common/lookups";
import { BillSearchContent, CollapsibleSection } from "components";

function BillSearch(props) {
    const [resPageSize, setResPageSize] = useState(5);
    const [chamberButtons, setChamberButtons] = useState({
        House: true,
        Senate: true,
    });
    const [versionButtons, setVersionButtons] = useState(initialVersionToFull);
    const [textBox, setTextBox] = useState("");
    const [sortField, setSortField] = useState("number");
    const [totalResults, setTotalResults] = useState(0);
    const [currentSearch, setCurrentSearch] = useState({
        congress: "118",
        chamber: "House,Senate",
        versions: Object.keys(versionToFull).join(","),
        text: "",
        sort: "number",
        page: 1,
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
    }

    useEffect(() => {
        executeSearch();
    }, [versionButtons, chamberButtons, sortField]);

    function innerPageRender(items) {
        const curPage = parseInt(currentSearch.page);

        return lodash.map(items, (n, i) => {
            return (
                <Button
                    key={`item-${i}`}
                    disabled={n === "..."}
                    minimal={n === "..."}
                    intent={n === curPage ? "primary" : ""}
                    onClick={() => {
                        setCurrentSearch({ ...currentSearch, page: n });
                    }}
                >
                    {n}
                </Button>
            );
        });
    }

    function renderPageList() {
        const totalPages = Math.ceil(totalResults / currentSearch.pageSize);
        const curPage = parseInt(currentSearch.page);
        if (totalPages < 6) {
            return (
                <div className="search-pager">
                    <div className="search-pager-buttons">
                        {" Page: "}
                        {innerPageRender(lodash.range(1, totalPages + 1))}
                    </div>
                </div>
            );
        } else {
            let sectionOne = lodash.range(1, 4);
            let sectionTwo = lodash.range(
                Math.max(curPage - 2, 1),
                Math.min(totalPages, curPage + 3),
            );
            let sectionThree = lodash.range(
                Math.max(totalPages - 3, 1),
                totalPages + 1,
            );
            sectionThree = lodash.filter(
                sectionThree,
                (i) => !sectionTwo.includes(i) && !sectionOne.includes(i),
            );
            sectionTwo = lodash.filter(
                sectionTwo,
                (i) => !sectionOne.includes(i),
            );
            let masterSection = [...sectionOne];
            if (sectionTwo.length > 0) {
                if (
                    masterSection[masterSection.length - 1] + 1 ===
                    sectionTwo[0]
                ) {
                    masterSection = [...masterSection, ...sectionTwo];
                } else {
                    masterSection = [...masterSection, "...", ...sectionTwo];
                }
            }
            if (sectionThree.length > 0) {
                if (
                    masterSection[masterSection.length - 1] + 1 ===
                    sectionThree[0]
                ) {
                    masterSection = [...masterSection, ...sectionThree];
                } else {
                    masterSection = [...masterSection, "...", ...sectionThree];
                }
            }
            return (
                <div className="search-pager">
                    <div className="search-pager-buttons">
                        {" Page: "}
                        {innerPageRender(masterSection)}
                    </div>
                </div>
            );
        }
    }

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
                {renderPageList()}
            </div>
        </Card>
    );
}

export default BillSearch;
