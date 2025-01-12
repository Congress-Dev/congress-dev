import React from "react";
import { Link } from "react-router-dom";
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
            interactive="true"
            elevation={Elevation.TWO}
        >
            <h2>
                <Link to={`/uscode/${usc_release_id}`}>{short_title}</Link>
            </h2>
            {long_title != "" && <p style={{ fontStyle: "italic" }}>{long_title}</p>}
            <p>Effective: {effective_date}</p>
            <Button>
                <a target="_blank" href={url}>
                    House.gov
                </a>
            </Button>
        </Callout>
    );
}

export default USCRevisionBox;
