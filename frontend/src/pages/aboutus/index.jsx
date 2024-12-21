import React from "react";

function AboutUs() {
  return (
    <>
      <h3 className="bp3-heading">About Us</h3>
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
    </>
  );
}

export default AboutUs;
