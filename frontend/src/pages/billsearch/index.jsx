import { Card, Elevation, FormGroup, InputGroup, Checkbox, Button, Divider, ControlGroup, HTMLSelect, ButtonGroup } from "@blueprintjs/core";
import { versionToFull } from "../../common/lookups";
import BillSearchContent from "../../components/billsearch";
import CollapseableSection from "../../components/collapseformgroup";
import React, { useState, useEffect } from "react";
import lodash from "lodash";
import qs from "query-string";

function BillSearch(props) {
  const [resPageSize, setResPageSize] = useState(5);
  const [chamberButtons, setChamberButtons] = useState({ House: true, Senate: true });
  const [versionButtons, setVersionButtons] = useState(versionToFull);
  const [textBox, setTextBox] = useState("Test");
  const [totalResults, setTotalResults] = useState(0);
  const [currentSearch, setCurrentSearch] = useState({
    congress: "118",
    chamber: "House,Senate",
    versions: Object.keys(versionToFull).join(","),
    text: "",
    page: 1,
    pageSize: resPageSize,
    ...qs.parse(props.location.search),
  });

  const [collapsed, setCollapsed] = useState(false); // State to control the signal

  function toggleCollapseAll() {
    setCollapsed(true);
  }
  function toggleExpandAll() {
    setCollapsed(false);
  }
  function toggleCheckAll() {
    setChamberButtons({ House: true, Senate: true });
    setVersionButtons(lodash.mapValues(versionToFull, () => {
      return true
    }));
  }

  function toggleUncheckAll() {
    setChamberButtons({ House: false, Senate: false });
    setVersionButtons(lodash.mapValues(versionToFull, () => {
      return false
    }));
  }

  function executeSearch() {
    setCurrentSearch({
      ...currentSearch,
      chamber: lodash
        .keys(lodash.pickBy(chamberButtons, value => value))
        .join(","),
      versions: lodash
        .keys(lodash.pickBy(versionButtons, value => value))
        .join(","),
      text: textBox,
    })
  }

  function innerPageRender(items) {
    const curPage = parseInt(currentSearch.page);

    return lodash.map(items, (n, i) => {
      return (
        <Button
          key={`item-${i}`}
          disabled={n === '...'}
          minimal={n === '...'}
          intent={
            (n === curPage ? "primary" : "")
          }
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
          Total Results: {totalResults}
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
        Math.min(totalPages, curPage + 3)
      );
      let sectionThree = lodash.range(Math.max(totalPages - 3, 1), totalPages);
      sectionThree = lodash.filter(sectionThree, i => !sectionTwo.includes(i));
      sectionTwo = lodash.filter(sectionTwo, i => !sectionOne.includes(i));
      let masterSection = [...sectionOne];
      if (sectionTwo.length > 0) {
        if (masterSection[masterSection.length - 1] + 1 === sectionTwo[0]) {
          masterSection = [...masterSection, ...sectionTwo];
        } else {
          masterSection = [...masterSection, "...", ...sectionTwo];
        }
      }
      if (sectionThree.length > 0) {
        if (masterSection[masterSection.length - 1] + 1 === sectionThree[0]) {
          masterSection = [...masterSection, ...sectionThree];
        } else {
          masterSection = [...masterSection, "...", ...sectionThree];
        }
      }
      return (
        <div className="search-pager">
          Total Results: {totalResults}
          <div className="search-pager-buttons">
            {" Page: "}
            {innerPageRender(masterSection)}
          </div>
        </div>
      );
    }
    return <span>Test {totalResults}</span>;
  }
  useEffect(() => {
    // Update the query string with our new things
    props.history.push({
      pathname: props.location.pathname,
      search: qs.stringify(currentSearch, { encode: false }),
    });
    let temp = {};
    lodash.forEach(currentSearch.versions.split(","), item => {
      temp[item] = true;
    });
    setVersionButtons(temp);
    temp = {};
    lodash.forEach(currentSearch.chamber.split(","), item => {
      temp[item] = true;
    });
    setChamberButtons(temp);
  }, [currentSearch]);
  useEffect(() => {
    setCurrentSearch({
      congress: "118",
      chamber: "House,Senate",
      versions: Object.keys(versionToFull).join(","),
      text: "",
      page: 1,
      pageSize: resPageSize,
      ...qs.parse(props.location.search),
    });
  }, [props.location.search]);
  return (
    <Card className="search-content" elevation={Elevation.ONE}>
      <div className="sidebar">
        <FormGroup label={"Search"} labelFor="text-input">
          <ControlGroup fill={true}>
            <HTMLSelect options={['Date', 'Name']} />
            <InputGroup
              value={textBox}
              onChange={event => {
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
        <ButtonGroup className="collapse-controls">
          <Button icon="collapse-all" onClick={toggleCollapseAll}></Button>
          <Button icon="expand-all" onClick={toggleExpandAll}></Button>
          <Button icon="add" onClick={toggleCheckAll}>Select All</Button>
          <Button icon="remove" onClick={toggleUncheckAll}>Deselect All</Button>
        </ButtonGroup>
        <CollapseableSection title="Session of Congress" collapsed={collapsed}></CollapseableSection>
        <CollapseableSection title="Chamber of Origin" collapsed={collapsed}>
          <Checkbox
            checked={chamberButtons.House === true}
            label="House"
            onChange={() => {
              setChamberButtons({ ...chamberButtons, House: !chamberButtons.House });
            }}
          />
          <Checkbox
            checked={chamberButtons.Senate === true}
            label="Senate"
            onChange={() => {
              setChamberButtons({ ...chamberButtons, Senate: !chamberButtons.Senate });
            }}
          />
        </CollapseableSection>
        <CollapseableSection title="Legislation Status" collapsed={collapsed}>
          {lodash.map(versionToFull, (value, key) => {
            return (
              <Checkbox
                key={`checkbox-${key}`}
                checked={versionButtons[key] === true}
                label={value}
                onChange={() => {
                  setVersionButtons({ ...versionButtons, [key]: !versionButtons[key] });
                }}
              />
            );
          })}
        </CollapseableSection>
      </div>
      <div className="content" style={{ paddingLeft: "20px" }}>
        <BillSearchContent
          congress={currentSearch.congress}
          chamber={currentSearch.chamber}
          versions={currentSearch.versions}
          text={currentSearch.text}
          page={currentSearch.page}
          pageSize={currentSearch.pageSize}
          setResults={setTotalResults}
        />
        {renderPageList()}
      </div>
    </Card>
  );
}

export default BillSearch;
