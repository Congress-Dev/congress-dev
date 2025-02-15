import React from "react";
import { withRouter, Link } from "react-router-dom";
import { Callout, SectionCard, Icon } from "@blueprintjs/core";

function LegislatorCard({ legislator }) {
    return (
        <SectionCard
            padded={false}
            className={`legislator-card ${legislator.party?.toLowerCase()}`}
        >
            <Callout>
                <div className="image">
                    {legislator.imageUrl != null && legislator.imageUrl != "" ? (
                        <img src={legislator.imageUrl} />
                    ) : (
                        <Icon icon="user" />
                    )}
                </div>
                <div className="details">
                    <h2 style={{ marginTop: "0px", marginBottom: "0px" }}>
                        <Link to={`/member/${legislator.bioguideId}`}>{`${legislator.lastName}, ${legislator.firstName}`}</Link>
                    </h2>
                    <div>
                        <b>Job:</b> {legislator.job ?? "Unknown"}
                    </div>
                    <div>
                        <b>Party:</b> {legislator.party ?? "Unknown"}
                    </div>
                    <div>
                        <b>State:</b> {legislator.state ?? "Unknown"}
                    </div>
                </div>
            </Callout>
        </SectionCard>
    );
}

export default withRouter(LegislatorCard);
