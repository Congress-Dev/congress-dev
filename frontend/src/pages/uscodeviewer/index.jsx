// Will hold a sidebar, and a main viewing area
import React, { useEffect, useState } from "react";

import USCSidebar from "components/uscsidebar";
import USCView from "components/uscview";

function USCodeViewer(props) {
  const [title, setTitle] = useState("01");
  const [section, setSection] = useState(null);
  console.log(props.match);
  const { uscReleaseId, uscTitle, uscSection } = props.match.params;
  console.log(window.innerHeight);
  return (
    <>
      <div className="sidebar" style={{height: `${window.innerHeight - 70}px`, overflow: 'auto'}}>
        <USCSidebar release={uscReleaseId} title={(uscTitle || "").replace("#", "")} section={uscSection} />
      </div>
      <div className="content">
        <USCView release={uscReleaseId} section={uscSection} title={uscTitle} />
      </div>
    </>
  );
}

export default USCodeViewer;
