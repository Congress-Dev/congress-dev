// Will hold a sidebar, and a main viewing area
import React, { useRef, useEffect } from "react";
import { Section, SectionCard, Callout } from "@blueprintjs/core";

import { USCSidebar, USCView } from "components";

function USCodeViewer(props) {
    const { uscReleaseId, uscTitle, uscSection } = props.match.params;
    const elementRef = useRef();

    useEffect(() => {
        const element = elementRef.current;
        if (element) {
            const yPosition = element.getBoundingClientRect().top + 35;
            document.documentElement.style.setProperty(
                "--usc-content-y-position",
                `${yPosition}px`,
            );
        }
    }, []);

    return (
        <Section
            className="page"
            title="United States Code"
            subtitle="The Foundation of U.S. Law"
        >
            <SectionCard>
                <div
                    className="sidebar"
                    style={{
                        overflow: "auto",
                    }}
                >
                    <USCSidebar
                        release={uscReleaseId}
                        title={(uscTitle || "").replace("#", "")}
                        section={uscSection}
                    />
                </div>
                <Section
                    compact={true}
                    className="content"
                    title={uscTitle}
                    subtitle={uscSection}
                    icon="drag-handle-vertical"
                >
                    <Callout>
                        <div className="usc-content" ref={elementRef}>
                            <USCView
                                release={uscReleaseId}
                                section={uscSection}
                                title={uscTitle}
                            />
                        </div>
                    </Callout>
                </Section>
            </SectionCard>
        </Section>
    );
}

export default USCodeViewer;
