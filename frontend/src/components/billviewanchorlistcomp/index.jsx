import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { md5 } from "common/other";
import { useHistory } from "react-router-dom";
function BillViewAnchorList(props) {
    const history = useHistory();
    const { anchors } = props;
    return <><p>Grey and crossed out means we detected it, but are unable to offer a jump to view of it at this moment</p>{
        lodash.map(anchors, (arr, ind) => {
            if (arr[1] !== undefined) {
                return <p className="anchor-list-link" key={ind} onClick={() => {
                    history.replace({ hash: arr[1] });
                    document.getElementById(arr[1]).scrollIntoView();
                }}>{arr[0]}</p>
            } else {
                return <p className="anchor-list-bad" key={ind} >{arr[0]}</p>
            }
        })
    }</>
}


export default BillViewAnchorList;