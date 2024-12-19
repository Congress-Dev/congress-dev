import React from "react";
import lodash from "lodash";
import { withRouter, Link } from "react-router-dom";

import { Card, Tag } from "@blueprintjs/core";

import { chamberLookup, versionToFull } from "../../common/lookups";

function BillCard(props) {
  const { bill } = props;
  function genTitle() {
    const { legislation_versions = [] } = bill;

    return (
      <>
        <Link
          to={`/bill/${bill.congress}/${bill.chamber}/${bill.number}/${legislation_versions[legislation_versions.length - 1].legislation_version}`}
        >
          {`${chamberLookup[bill.chamber]} ${bill.number}`}
        </Link>
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
            <Link
              to={`/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers.legislation_version}`}
              key={`item-${ind}`}
            >
              {versionToFull[vers.legislation_version.toLowerCase()]}
            </Link>
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
      <h2 style={{ marginTop: "0px" }}>{genTitle()}</h2>
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
