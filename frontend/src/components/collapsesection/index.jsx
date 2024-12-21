import React, { useState, useEffect } from "react";

import { Collapse, Icon } from "@blueprintjs/core";

function CollapseableSection(props) {
    const [isOpen, setIsOpen] = useState(true);

    useEffect(() => {
        setIsOpen(!props.collapsed);
    }, [props.collapsed]);

    function renderIcon() {
        if (isOpen) {
            return <Icon icon="unarchive" />;
        }
        return <Icon icon="archive" />;
    }
    return (
        <div className="collapse-wrapper">
            <span onClick={() => setIsOpen(!isOpen)}>
                {renderIcon()} - {props.title || "Toggle"}
            </span>
            <Collapse className="collapse-section" isOpen={isOpen}>
                {props.children}
            </Collapse>
        </div>
    );
}

export default CollapseableSection;
