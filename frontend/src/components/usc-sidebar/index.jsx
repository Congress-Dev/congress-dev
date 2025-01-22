// Renders the sidebar for the applicable location we are in.
import React, { useEffect, useState } from "react";
import { withRouter } from "react-router-dom";

import { HTMLSelect, Label } from "@blueprintjs/core";

import {
    getUSCTitleList,
    getUSCSectionList,
    getUSCLevelSections,
    getUSCSectionLineage,
} from "common/api";

function USCSidebar(props) {
    const [levelOne, setLevelOne] = useState(null);
    const [selectionOne, setSelectionOne] = useState(null);

    useEffect(() => {
        getUSCTitleList(props.release).then((res) => {
            const options = res.map((level) => {
                return {
                    label: `${level.short_title}. ${level.long_title}`,
                    value: level.short_title,
                };
            });

            setLevelOne(options);
            setSelectionOne(options[0].value);
        });
    }, []);

    useEffect(() => {
        if (selectionOne == null) {
            return;
        }

        props.history.push(
            `/uscode/${props.release}/${selectionOne}`
        )
    }, [selectionOne]);

    function handleLevelOne(e) {
        setSelectionOne(e.currentTarget.value)
    }

    return (
        <>
            {levelOne && (
                <Label>
                    Section:
                    <HTMLSelect
                        fill={true}
                        options={levelOne}
                        onChange={handleLevelOne}
                    ></HTMLSelect>
                </Label>
            )}       
        </>
    );
}

export default withRouter(USCSidebar);
