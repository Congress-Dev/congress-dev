import React from "react";
import lodash from "lodash";
import { withRouter } from "react-router-dom";

import { Card, Tag } from "@blueprintjs/core";

import { chamberLookup, versionToFull } from "common/lookups";

function BillCard(props) {
  const { bill } = props;
  function genTitle() {
    return (
      <>
        <a
          href={`https://congress.gov/bill/${bill.congress}-congress/${bill.chamber}-bill/${bill.number}`}
        >
          {`${chamberLookup[bill.chamber]} ${bill.number}`}
        </a>
        <Tag minimal={true}>Congress.gov</Tag>
      </>
    );
  }
  function getFirstEffectiveDate() {
    const { legislation_versions = [] } = bill;
    const dateStr = legislation_versions[0].effective_date;
    return `${dateStr}`;
  }
  function renderVersions() {
    const { legislation_versions = [] } = bill;
    const len = legislation_versions.length;
    return (
      <>
        {lodash.map(legislation_versions, (vers, ind) => {
          const anchorObj = (
            <a
              href={`/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.legislation_version}`}
              key={`item-${ind}`}
            >
              {versionToFull[vers.legislation_version.toLowerCase()]}
            </a>
          );
          if (ind < len - 1) {
            return (
              <>
                {anchorObj}
                <span>{" >> "}</span>
              </>
            );
          } else {
            return anchorObj;
          }
        })}
      </>
    );
  }
  return (
    <Card>
      <h2 style={{marginTop: "0px"}}>{genTitle()}</h2>
      <span style={{ fontStyle: "italic" }}>{bill.title}</span>
      <br />
      <span className="bill-card-introduced-date">
        <span style={{ fontWeight: "bold" }}>First Introduced:</span>{" "}
        {getFirstEffectiveDate()}
      </span>
      <br />
      {renderVersions()}
    </Card>
  );
}

export default withRouter(BillCard);
