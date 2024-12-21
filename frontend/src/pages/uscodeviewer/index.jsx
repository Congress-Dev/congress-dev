// Will hold a sidebar, and a main viewing area
import React from "react";
import { Card, Callout } from "@blueprintjs/core";

import { USCSidebar, USCView } from "../../components";

function USCodeViewer(props) {
    const { uscReleaseId, uscTitle, uscSection } = props.match.params;

    return (
        <Card className="page">
            <div
                className="sidebar"
                style={{
                    height: `${window.innerHeight - 70}px`,
                    overflow: "auto",
                }}
            >
                <USCSidebar
                    release={uscReleaseId}
                    title={(uscTitle || "").replace("#", "")}
                    section={uscSection}
                />
            </div>
            <div className="content">
                <Callout>
                    <USCView
                        release={uscReleaseId}
                        section={uscSection}
                        title={uscTitle}
                    />
                </Callout>
            </div>
        </Card>
    );
}

export default USCodeViewer;
