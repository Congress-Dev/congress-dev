import { Card, Elevation, FormGroup, InputGroup, Checkbox } from "@blueprintjs/core";
import { versionToFull } from "common/lookups";
import BillSearchContent from "components/billsearch";
import CollapseableSection from "components/collapseformgroup";
import React, { useState } from "react";
import lodash from "lodash";

function BillSearch() {
  const [chamberButtons, setChamberButtons] = useState({House: true, Senate: true});
  const [versionButtons, setVersionButtons] = useState(versionToFull);
  const [textBox, setTextBox] = useState("Test");
  const [currentSearch, setCurrentSearch] = useState({
    congress: "116",
    chamber: "House,Senate",
    versions: Object.keys(versionToFull).join(","),
    text: "",
    page: 1,
    pageSize: 25,
  });
  console.log(currentSearch);
  return (
    <Card className="search-content" elevation={Elevation.ONE}>
      <div className="sidebar">
        <FormGroup label={"Search"} labelFor="text-input">
          <InputGroup
          value={textBox}
            onChange={(event) => {
              setTextBox(event.target.value);
            }}
            rightElement={
              <button
                class="bp3-button bp3-minimal bp3-intent-primary bp3-icon-arrow-right"
                onClick={() => {
                  setCurrentSearch({
                    ...currentSearch,
                    chamber: lodash
                      .keys(lodash.pickBy(chamberButtons, value => value))
                      .join(","),
                    versions: lodash
                      .keys(lodash.pickBy(versionButtons, value => value))
                      .join(","),
                      text: textBox
                  });
                }}
              ></button>
            }
          />
        </FormGroup>
        <CollapseableSection title="Chamber">
          <Checkbox
            checked={chamberButtons.House}
            label="House"
            onChange={() => {
              setChamberButtons({ ...chamberButtons, House: !chamberButtons.House });
            }}
          />
          <Checkbox
            checked={chamberButtons.Senate}
            label="Senate"
            onChange={() => {
              setChamberButtons({ ...chamberButtons, Senate: !chamberButtons.Senate });
            }}
          />
        </CollapseableSection>
        <CollapseableSection title="Versions">
          {lodash.map(versionToFull, (value, key) => {
            return (
              <Checkbox
                key={`checkbox-${key}`}
                checked={versionButtons[key]}
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
