import lodash from "lodash";

function capFirstLetter(str) {
  return str.charAt(0).toUpperCase() + str.substring(1);
}

export const endpoint = "http://localhost:9090";

export const getBillSummary = (congress, chamber, billNumber) => {
  return fetch(
    `${endpoint}/congress/${congress}/${capFirstLetter(chamber)}-bill/${billNumber}`
  ).then(res => res.json());
};

export const getBillVersionText = (congress, chamber, billNumber, billVersion) => {
  // Grab the bill text, and then put it into the nested format
  // TODO: Move this treeification to the server?
  return fetch(
    `${endpoint}/congress/${congress}/${chamber.toLowerCase()}-bill/${billNumber}/${billVersion}/text`
  )
    .then(res => res.json())
    .then(flatJson => {
      let looped = {};
      const sorted = lodash.sortBy(
        flatJson.content,
        ({ legislation_content_id, order_number }) =>
          `${legislation_content_id}.${order_number.toString().padStart(3, "0")}`
      );
      if(sorted.length == 0){
          return {};
      }
      lodash.forEach(sorted, obj => {
        let copyObj = { ...obj, children: [] };
        looped[copyObj.legislation_content_id] = copyObj;
        if (copyObj.parent_id) {
          looped[copyObj.parent_id].children.push(copyObj);
        }
      });
      return looped[sorted[0].legislation_content_id];
    });
};
