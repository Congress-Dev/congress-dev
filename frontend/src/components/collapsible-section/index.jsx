import React, { useState, useEffect } from "react";
import { Collapse, Icon } from "@blueprintjs/core";

function CollapsibleSection(props) {
    const [isOpen, setIsOpen] = useState(true);

    useEffect(() => {
        setIsOpen(!props.collapsed);
    }, [props.collapsed]);

    return (
        <div className="collapse-wrapper">
            <span onClick={() => setIsOpen(!isOpen)}>
                <Icon icon={isOpen ? "unarchive" : "archive"} /> -{" "}
                {props.title || "Toggle"}
            </span>
            <Collapse className="collapse-section" isOpen={isOpen}>
                {props.children}
            </Collapse>
        </div>
    );
}

export default CollapsibleSection;
