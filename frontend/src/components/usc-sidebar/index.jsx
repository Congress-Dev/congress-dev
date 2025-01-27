// Renders the sidebar for the applicable location we are in.
import React, { useEffect, useState } from "react";
import { withRouter } from "react-router-dom";

import { Label, SectionCard, HTMLSelect } from "@blueprintjs/core";

function USCSidebar(props) {
    const [chapterSelection, setChapterSelection] = useState(props.title);
    const [subchapterSelection, setSubchapterSelection] = useState(null);

    useEffect(() => {
        if (chapterSelection == null) {
            return;
        }

        props.history.push(
            `/uscode/${props.release}/${chapterSelection}`
        )
    }, [chapterSelection]);

    function handleLevelOne(e) {
        setChapterSelection(e.currentTarget.value)
    }

    function handleLevelTwo(e) {
        setSubchapterSelection(e.currentTarget.value)
    }

    return (
        <>
            <SectionCard>
                <div className="section-detail">
                    <span className="section-detail-label">Version:</span>
                    <span className="section-detail-value">
                        { props.activeRevision.short_title }
                    </span>
                </div>

                <div className="section-detail">
                    <span className="section-detail-label">Effective:</span>
                    <span className="section-detail-value">
                        { props.activeRevision.effective_date }
                    </span>
                </div>
            </SectionCard>

            <SectionCard>
            {props.chapters && (
                <Label>
                    Section:
                    <HTMLSelect
                        fill={true}
                        options={props.chapters}
                        onChange={handleLevelOne}
                        value={chapterSelection}
                    ></HTMLSelect>
                </Label>
            )}
            {props.subchapters && (
                <Label>
                    Chapter:
                    <HTMLSelect
                        fill={true}
                        options={props.subchapters}
                        onChange={handleLevelTwo}
                        value={subchapterSelection}
                    ></HTMLSelect>
                </Label>
            )}
            </SectionCard>
        </>
    );
}

export default withRouter(USCSidebar);
