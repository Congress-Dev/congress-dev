import React from "react";

import { Card, Callout } from "@blueprintjs/core";

function AboutUs() {
  return (
    <Card className="page">
      <h3 className="bp5-heading">About Us</h3>
      <p>The source for our data is from official government websites</p>
      <ul>
        <li>
          <a href="https://www.govinfo.gov/bulkdata" target="_blank" rel="noopener noreferrer">
            Bill Text/Statuses
          </a>
        </li>
        <li>
          <a
            href="https://uscode.house.gov/download/priorreleasepoints.htm"
            target="_blank" rel="noopener noreferrer"
          >
            USCode Text
          </a>
        </li>
      </ul>

      <h3 class="bp5-heading">Contact Us</h3>
      <ul>
        <li>
          <a href="mailto:admin@congress.dev">Admin</a>
        </li>
      </ul>
    </Card>
  );
}

export default AboutUs;
