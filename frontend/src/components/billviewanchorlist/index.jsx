import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { md5 } from "../../common/other";
import { useHistory } from "react-router-dom";
function BillViewAnchorList(props) {
  const history = useHistory();
  const { anchors } = props;
  return <><p>Grey and crossed out means we detected it, but are unable to offer a jump to view of it at this moment</p>{
    lodash.map(anchors, (arr, ind) => {
      if (arr.hash !== undefined) {
        return <p className="anchor-list-link" key={ind} onClick={() => {
          history.replace({ hash: arr.hash });
          document.getElementById(arr.hash).scrollIntoView();
        }}>{arr.title}</p>
      } else {
        return <p className="anchor-list-bad" key={ind} >{arr.title}</p>
      }
    })
  }</>
}


export default BillViewAnchorList;