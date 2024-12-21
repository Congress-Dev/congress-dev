import React, { useState } from "react";
import { Collapse, Icon } from "@blueprintjs/core";

function CollapseableSection({ title, collapsed, ...props }) {
    const [isOpen, setIsOpen] = useState(collapsed);

    return (
        <div className="collapse-wrapper">
            <span onClick={() => setIsOpen(!isOpen)}>
                <Icon icon={isOpen ? 'unarchive' : 'archive'} /> - {title || "Toggle"}
            </span>
            <Collapse className="collapse-section" isOpen={isOpen}>
                {props.children}
            </Collapse>
        </div>
    );
}

export default CollapseableSection;
