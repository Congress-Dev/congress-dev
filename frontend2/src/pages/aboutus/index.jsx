import React from "react";

function AboutUs() {
  return (
    <>
      <h3 class="bp3-heading">About Us</h3>
      <p>The source for our data is from official government websites</p>
      <ul>
        <li>
          <a href="https://www.govinfo.gov/bulkdata" target="_blank">
            Bill Text/Statuses
          </a>
        </li>
        <li>
          <a
            href="https://uscode.house.gov/download/priorreleasepoints.htm"
            target="_blank"
          >
            USCode Text
          </a>
        </li>
      </ul>
    </>
  );
}

export default AboutUs;
