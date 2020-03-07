import React, { useState } from "react";

import { Collapse, Icon } from "@blueprintjs/core";

function CollapseableSection(props) {
  const [isOpen, setIsOpen] = useState(true);
  function renderIcon(){
    if(isOpen){
      return <Icon icon="unarchive" />;
    }
    return  <Icon icon="archive" />;
  }
  return (
    <>
      <span onClick={() => setIsOpen(!isOpen)}>{renderIcon()} - {props.title || "Toggle"}</span>
      <Collapse isOpen={isOpen}>{props.children}</Collapse>
    </>
  );
}

export default CollapseableSection;
