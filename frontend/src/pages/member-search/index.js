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
import { CollapsibleSection, Paginator, LegislatorSearchContent } from "components";

function MemberSearch(props) {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);

  const decoded = decodeSelections(searchParams.get("selections"));

  const [isFirstRender, setFirstRender] = useState(true);
  const [resPageSize, setResPageSize] = useState(5);
  const [chamberButtons, setChamberButtons] = useState(decoded.chamber);
  const [versionButtons, setVersionButtons] = useState(decoded.versions);
  const [textBox, setTextBox] = useState(searchParams.get("text") || "");
  const [totalResults, setTotalResults] = useState(0);

  const [currentSearch, setCurrentSearch] = useState({
      congress: searchParams.get("congress") || "118,119",
      chamber: lodash
          .keys(lodash.pickBy(chamberButtons, (value) => value))
          .join(","),
      state: lodash
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
      if (
          params.congress != null &&
          currentSearch.congress != params.congress
      ) {
          updated = true;
          newSearch = {
              ...newSearch,
              congress: params.congress,
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
      if (currentSearch.congress == "" && params.congress != null) {
          updated = true;
          delete params.congress;
      } else if (
          currentSearch.congress != "" &&
          params.congress != currentSearch.congress
      ) {
          updated = true;
          params.congress = currentSearch.congress;
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
  }, [versionButtons, chamberButtons]);

  function setCurrentSort(sort) {
      setCurrentSearch({
          ...currentSearch,
          page: 1,
          sort: sort,
      });
  }
    return (
        <Section
            className="page"
            elevation={Elevation.ONE}
            title="Member Search"
            subtitle="Search for members by state or party"
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
                    </ButtonGroup>
                    <CollapsibleSection
                        title="Session of Congress"
                        collapsed={collapsed}
                    >
                        <Checkbox
                            checked={currentSearch.congress.includes("119")}
                            label="119th"
                            onChange={() => {
                                const cong = currentSearch.congress
                                    .split(",")
                                    .filter((value) => {
                                        return value != "";
                                    });
                                if (cong.includes("119")) {
                                    setCurrentSearch({
                                        ...currentSearch,
                                        congress: cong
                                            .filter((value) => {
                                                return (
                                                    value != "119" &&
                                                    value != ""
                                                );
                                            })
                                            .join(","),
                                    });
                                } else {
                                    cong.push("119");
                                    setCurrentSearch({
                                        ...currentSearch,
                                        congress: cong.join(","),
                                    });
                                }
                            }}
                        />
                        <Checkbox
                            checked={currentSearch.congress.includes("118")}
                            label="118th"
                            onChange={() => {
                                const cong = currentSearch.congress
                                    .split(",")
                                    .filter((value) => {
                                        return value != "";
                                    });
                                if (cong.includes("118")) {
                                    setCurrentSearch({
                                        ...currentSearch,
                                        congress: cong
                                            .filter((value) => {
                                                return value != "118";
                                            })
                                            .join(","),
                                    });
                                } else {
                                    cong.push("118");
                                    setCurrentSearch({
                                        ...currentSearch,
                                        congress: cong.join(","),
                                    });
                                }
                            }}
                        />
                    </CollapsibleSection>
                    <CollapsibleSection
                        title="Chamber"
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
                        title="State"
                        collapsed={collapsed}
                    >

                    </CollapsibleSection>
                </div>
                <Section
                    title="Results"
                    subtitle={`${totalResults.toLocaleString()} Legislators`}
                    className="content"
                    icon="inbox-search"
                    // rightElement={
                    //     <>
                    //         <Icon icon="sort-alphabetical" /> Sort:
                    //         <HTMLSelect
                    //             value={currentSearch.sort}
                    //             options={[
                    //             ]}
                    //             onChange={(event) => {
                    //                 setCurrentSort(event.currentTarget.value);
                    //             }}
                    //         />
                    //     </>
                    // }
                >
                    <LegislatorSearchContent
                        name={currentSearch.text}
                        chamber={currentSearch.chamber}
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

export default MemberSearch;
