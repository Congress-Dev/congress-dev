import { Card, Elevation, FormGroup, InputGroup, Checkbox } from "@blueprintjs/core";
import { versionToFull } from "common/lookups";
import BillSearchContent from "components/billsearch";
import CollapseableSection from "components/collapseformgroup";
import React, { useState, useEffect } from "react";
import lodash from "lodash";
import qs from "query-string";

function BillSearch(props) {
  const [chamberButtons, setChamberButtons] = useState({ House: true, Senate: true });
  const [versionButtons, setVersionButtons] = useState(versionToFull);
  const [textBox, setTextBox] = useState("Test");
  const [currentSearch, setCurrentSearch] = useState({
    congress: "116",
    chamber: "House,Senate",
    versions: Object.keys(versionToFull).join(","),
    text: "",
    page: 1,
    pageSize: 25,
    ...qs.parse(props.location.search),
  });
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
      congress: "116",
      chamber: "House,Senate",
      versions: Object.keys(versionToFull).join(","),
      text: "",
      page: 1,
      pageSize: 25,
      ...qs.parse(props.location.search),
    });
  }, [props.location.search]);
  return (
    <Card className="search-content" elevation={Elevation.ONE}>
      <div className="sidebar">
        <FormGroup label={"Search"} labelFor="text-input">
          <InputGroup
            value={textBox}
            onChange={event => {
              setTextBox(event.target.value);
            }}
            rightElement={
              <button
                className="bp3-button bp3-minimal bp3-intent-primary bp3-icon-arrow-right"
                onClick={() => {
                  setCurrentSearch({
                    ...currentSearch,
                    chamber: lodash
                      .keys(lodash.pickBy(chamberButtons, value => value))
                      .join(","),
                    versions: lodash
                      .keys(lodash.pickBy(versionButtons, value => value))
                      .join(","),
                    text: textBox,
                  });
                }}
              ></button>
            }
          />
        </FormGroup>
        <CollapseableSection title="Session of Congress">

        </CollapseableSection>
        <CollapseableSection title="Chamber of Origin">
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
        <CollapseableSection title="Legislation Status">
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
        />
      </div>
    </Card>
  );
}

export default BillSearch;
