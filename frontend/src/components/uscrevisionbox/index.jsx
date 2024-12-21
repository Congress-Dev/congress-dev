// Tiny component for holding information about a single USC Revision point

import React, { useEffect, useState } from "react";

import { Button, Callout, Elevation } from "@blueprintjs/core";

function USCRevisionBox({
  usc_release_id,
  effective_date,
  long_title,
  short_title,
  url,
}) {
  return (
    <Callout
      id={`usc-release-box-${usc_release_id}`}
      className="usc-release-box"
      interactive={true}
      elevation={Elevation.TWO}
    >
      <h2><a href={`/uscode/${usc_release_id}`}>{short_title}</a></h2>
      <p style={{ fontStyle: "italic" }}>{long_title}</p>
      <p>Effective: {effective_date}</p>
      <Button><a href={url}>House.gov</a></Button>
    </Callout>
  );
}

export default USCRevisionBox;
