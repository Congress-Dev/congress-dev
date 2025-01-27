// Will hold a sidebar, and a main viewing area
import React, { useRef, useEffect, useState, useMemo } from "react";
import { Section, SectionCard, Callout } from "@blueprintjs/core";

import {
    getUSCTitleList,
    getUSCLevelSections,
    getUSCRevisions,
} from "common/api";
import { USCSidebar, USCView } from "components";

function USCodeViewer(props) {
    const { uscReleaseId, uscTitle, uscSection } = props.match.params;
    const elementRef = useRef();

    const [revisions, setRevisions] = useState(null);
    const [chapters, setChapters] = useState(null);
    const [subchapters, setSubchapters] = useState(null);

    const activeRevision = useMemo(() => {
        if (revisions == null) {
            return;
        }

        for (const revision of revisions) {
            if (revision.usc_release_id == uscReleaseId) {
                return revision;
            }
        }
    }, [revisions]);

    const chapterMap = useMemo(() => {
        if (chapters == null) {
            return;
        }

        const map = {};
        for (let chapter of chapters) {
            map[chapter.value] = chapter.label;
        }
        return map;
    }, [chapters]);

    useEffect(() => {
        const element = elementRef.current;
        if (element) {
            const yPosition = element.getBoundingClientRect().top + 75;
            document.documentElement.style.setProperty(
                "--usc-content-y-position",
                `${yPosition}px`,
            );
        }
    }, [elementRef.current]);

    useEffect(() => {
        getUSCRevisions().then(setRevisions);

        getUSCTitleList(uscReleaseId).then((res) => {
            const options = res.map((level) => {
                return {
                    label: `${level.short_title}. ${level.long_title}`,
                    value: level.short_title,
                };
            });

            setChapters(options);
        });

        getUSCLevelSections(uscReleaseId, uscTitle).then((res) => {
            console.log(res);
            const options = res.map((level) => {
                return {
                    label: `${level.number}. ${level.heading}`,
                    value: level.usc_chapter_id,
                };
            });

            setSubchapters(options);
        });
    }, []);

    useEffect(() => {
        getUSCLevelSections(uscReleaseId, uscTitle).then((res) => {
            console.log(res);
            const options = res.map((level) => {
                return {
                    label: `${level.number}. ${level.heading}`,
                    value: level.usc_chapter_id,
                };
            });

            setSubchapters(options);
        });
    }, [uscTitle])

    return (
        <Section
            className="page"
            title="United States Code"
            subtitle="The Foundation of U.S. Law"
        >
            {activeRevision && (
                <SectionCard>
                    <div
                        className="sidebar"
                        style={{
                            overflow: "auto",
                        }}
                    >
                        <USCSidebar
                            activeRevision={activeRevision}
                            chapters={chapters}
                            subchapters={subchapters}
                            release={uscReleaseId}
                            title={(uscTitle || "").replace("#", "")}
                            section={uscSection}
                        />
                    </div>
                    <Section
                        compact={true}
                        className="content"
                        title={chapterMap != null ? chapterMap[uscTitle] : ""}
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
            )}
        </Section>
    );
}

export default USCodeViewer;
