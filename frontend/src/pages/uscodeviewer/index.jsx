// Will hold a sidebar, and a main viewing area
import React, { useEffect, useState } from "react";

import { Card, Callout } from "@blueprintjs/core";

import USCSidebar from "../../components/uscsidebar";
import USCView from "../../components/uscview";

function USCodeViewer(props) {
  const [title, setTitle] = useState("01");
  const [section, setSection] = useState(null);
  const { uscReleaseId, uscTitle, uscSection } = props.match.params;

  return (
    <Card className="page">
      <div className="sidebar" style={{ height: `${window.innerHeight - 70}px`, overflow: 'auto' }}>
        <USCSidebar release={uscReleaseId} title={(uscTitle || "").replace("#", "")} section={uscSection} />
      </div>
      <div className="content">
        <Callout>
          <USCView release={uscReleaseId} section={uscSection} title={uscTitle} />
        </Callout>
      </div>
    </Card>
  );
}

export default USCodeViewer;
