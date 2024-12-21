import React from "react";
import { useHistory } from "react-router-dom";
import lodash from "lodash";

function BillViewAnchorList({ anchors }) {
    const history = useHistory();

    return (
        <>
            <p>
                Grey and crossed out means we detected it, but are unable to
                offer a jump to view of it at this moment
            </p>
            {lodash.map(anchors, (arr, ind) => {
                if (arr.hash !== undefined) {
                    return (
                        <p
                            className="anchor-list-link"
                            key={ind}
                            onClick={() => {
                                history.replace({ hash: arr.hash });
                                document
                                    .getElementById(arr.hash)
                                    .scrollIntoView();
                            }}
                        >
                            {arr.title}
                        </p>
                    );
                } else {
                    return (
                        <p className="anchor-list-bad" key={ind}>
                            {arr.title}
                        </p>
                    );
                }
            })}
        </>
    );
}

export default BillViewAnchorList;
