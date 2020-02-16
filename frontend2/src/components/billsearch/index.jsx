// Handles searching the API for bills matching the criteria
import React, { useEffect, useState, useRef } from "react";
import lodash from "lodash";

import BillCard from "components/billcard";

import { getCongressSearch } from "common/api";

function BillSearchContent(props) {
  const [billList, setBillList] = useState([]);
  const e = useRef();

  useEffect(() => {
    getCongressSearch(
      props.congress,
      props.chamber,
      props.versions,
      props.text,
      props.page,
      props.pageSize
    ).then(setBillList);
  }, [
    props.congress,
    props.chamber,
    props.versions,
    props.text,
    props.page,
    props.pageSize,
  ]);
  function renderCardList(billItem, ind) {
    return <BillCard bill={billItem} key={`bill-search-list-${ind}`} />;
  }
  return <>{lodash.map(billList, renderCardList)}</>;
}

export default BillSearchContent;
