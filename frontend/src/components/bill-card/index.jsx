import React from "react";
import lodash, { map } from "lodash";
import { withRouter, Link } from "react-router-dom";
import { Callout, Breadcrumbs, Breadcrumb, Button, Tag } from "@blueprintjs/core";

import { chamberLookup, versionToFull } from "common/lookups";
const USDollar = new Intl.NumberFormat('en-US', {
  style: 'currency',
  currency: 'USD',
  maximumFractionDigits: 0, 
  minimumFractionDigits: 0, 
});
function BillCard({ bill }) {
  function genTitle() {
    const { legislation_versions = [] } = bill;

    return (
      <>
        <Link
          to={`/bill/${bill.congress}/${bill.chamber}/${bill.number}/${legislation_versions[legislation_versions.length - 1]}`}
        >
          {`${chamberLookup[bill.chamber]} ${bill.number}`}
        </Link>
      </>
    );
  }


  function renderVersions() {
    const { legislation_versions = [] } = bill;
    return (
      <Breadcrumbs
        className="bill-versions"
        breadcrumbRenderer={({ text, link, ...rest }) => (
          <Breadcrumb {...rest}>
            <Link to={link}>{text}</Link>
          </Breadcrumb>
        )}
        items={lodash.map(legislation_versions, (vers, ind) => {
          return {
            text: versionToFull[
              vers.toLowerCase()
            ],
            link: `/bill/${bill.congress}/${bill.chamber}/${bill.number}/${vers}`,
          };
        })}
      />
    );
  }
  function renderTags() {
    return <>{bill.tags.map(tag => <><Tag>{tag}</Tag>{'  '}</>)}</>
  }
  return (
    <Callout className="bill-card">
      <Button
        className="congress-link"
        icon="share"
        onClick={() => {
          window.open(
            `https://congress.gov/bill/${bill.congress}-congress/${bill.chamber}-bill/${bill.number}`,
            "_blank",
          );
        }}
      />
      <h2 style={{ marginTop: "0px", marginBottom: "0px" }}>
        {genTitle()} - {bill.title}
      </h2>
      <span className="bill-card-introduced-date">
        <span style={{ fontWeight: "bold" }}>Introduced:</span>{" "}
        {bill.effective_date}
      </span>
      <br />
      <span style={{ fontWeight: "bold" }}>Tags:</span>{renderTags()}
      <br />
      <span style={{ fontWeight: "bold" }}>Versions:</span>{" "}
      {renderVersions()}
      <br />
      {bill.appropriations ?  <><span style={{ fontWeight: "bold" }}>Appropriations:</span>{" "}{USDollar.format(bill.appropriations)} </>: null
}
        </Callout >
    );
}

export default withRouter(BillCard);
