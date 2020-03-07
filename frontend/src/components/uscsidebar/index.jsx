// Renders the sidebar for the applicable location we are in.
import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { withRouter } from 'react-router-dom';
import { Breadcrumbs, Boundary } from "@blueprintjs/core";

import { getUSCTitleList, getUSCSectionList } from "common/api";

function USCSidebar(props) {
  const [titleList, setTitleList] = useState([]);
  const [sectionList, setSectionList] = useState([]);
  useEffect(() => {
    if (!props.title) {
      getUSCTitleList(props.release).then(setTitleList);
    } else {
      getUSCSectionList(props.release, props.title).then(setSectionList);
    }
  }, [props.release, props.title]);
  let breadCrumbs = [{ href: "/uscode", text: "USCode" }];
  if (props.release) {
    breadCrumbs.push({
      href: `/uscode/${props.release}`,
      text: `Release ${props.release}`,
    });
  }
  if (props.title) {
    breadCrumbs.push({
      href: `/uscode/${props.release}/${props.title}`,
      text: `Title ${props.title}`,
    });
  }
  function navigate(url) {
    props.history.push(url);
  }
  console.log(titleList);
  // Only the release id given
  if (!props.title) {
    return (
      <>
        <Breadcrumbs collapseFrom={Boundary.START} items={breadCrumbs} /> <br />
        {lodash.map(titleList, (obj, ind) => (
          <p key={ind} className="sidebar-link">
            <a
              href="#"
              onClick={() => {
                navigate(`/uscode/${props.release}/${obj.short_title}`);
              }}
            >
              {obj.long_title}
            </a>
          </p>
        ))}
      </>
    );
  }
  return (
    <>
      <Breadcrumbs collapseFrom={Boundary.START} items={breadCrumbs} /> <br />
      {lodash.map(sectionList, (obj, ind) => (
        <p key={ind}>
          <a
            href="#"
            onClick={() => {
              navigate(`/uscode/${props.release}/${props.title}/${obj.number}`);
            }}
          >
            {obj.heading}
          </a>
        </p>
      ))}
    </>
  );
}

export default withRouter(USCSidebar);
