import lodash from "lodash";

export const capFirstLetter = function(str) {
  return str.charAt(0).toUpperCase() + str.substring(1);
}

let endP = "http://localhost:9090";
if(window.location.href.includes("congress.dev")){
  endP = "https://api.congress.dev"
}
export const endpoint = endP;

export const getBillSummary = (congress, chamber, billNumber) => {
  return fetch(
    `${endpoint}/congress/${congress}/${capFirstLetter(chamber)}-bill/${billNumber}`
  ).then(res => res.json());
};

export const getBillVersionText = (congress, chamber, billNumber, billVersion) => {
  // Grab the bill text, and then put it into the nested format
  // TODO: Move this treeification to the server?
  return fetch(
    `${endpoint}/congress/${congress}/${chamber.toLowerCase()}-bill/${billNumber}/${billVersion}/text?include_parsed=true`
  )
    .then(res => res.json())
    .then(flatJson => {
      let looped = {};
      const sorted = lodash.sortBy(
        flatJson.content,
        ({ legislation_content_id, order_number }) =>
          `${legislation_content_id}.${order_number.toString().padStart(3, "0")}`
      );
      if (sorted.length === 0) {
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

export const getUSCRevisions = () => {
  // Grab the list of USCode revision points from the server
  return fetch(`${endpoint}/usc/releases`)
    .then(res => res.json())
    .then(obj => obj.releases);
};

export const getUSCTitleList = uscReleaseId => {
  return fetch(`${endpoint}/usc/${uscReleaseId}/titles`)
    .then(res => res.json())
    .then(({ titles }) => lodash.sortBy(titles, "short_title"));
};

export const getUSCSectionList = (uscReleaseId, shortTitle) => {
  return fetch(`${endpoint}/usc/${uscReleaseId}/${shortTitle}/sections`)
    .then(res => res.json())
    .then(({ sections }) => lodash.sortBy(sections, "number"));
};

export const getUSCSectionContent = (uscReleaseId, shortTitle, sectionNumber) => {
  return fetch(`${endpoint}/usc/${uscReleaseId}/${shortTitle}/${sectionNumber}/text`)
    .then(res => res.json())
    .then(flatJson => {
      let looped = {};
      const sorted = lodash.sortBy(
        flatJson.content,
        ({ usc_content_id, order_number }) =>
          `${usc_content_id}.${order_number.toString().padStart(3, "0")}`
      );
      if (sorted.length === 0) {
        return {};
      }
      lodash.forEach(sorted, obj => {
        let copyObj = { ...obj, children: [] };
        looped[copyObj.usc_content_id] = copyObj;
        if (copyObj.parent_id) {
          looped[copyObj.parent_id].children.push(copyObj);
        }
      });
      return { children: [looped[sorted[0].usc_content_id]] };
    });
};

export const getCongressSearch = (
  congress,
  chamber,
  versions,
  text,
  page,
  pageSize
) => {
  return fetch(
    `${endpoint}/congress/search?congress=${congress || "None"}&chamber=${chamber ||
      "None"}&versions=${versions || ""}&text=${text}&page=${page}&pageSize=${pageSize}`
  )
    .then(res => res.json())
    .then(obj => obj.legislation);
};

export const getBillVersionDiffSummary = (session, chamber, bill, version) => {
  return fetch(
    `${endpoint}/congress/${session}/${chamber.toLowerCase()}-bill/${bill}/${version}/diffs`
  )
    .then(res => {
      if(res.status !== 200){
        return {};
      }
      return res.json();
    })
}

export const getBillVersionDiffForSection = (session, chamber, bill, version, uscTitle, uscSection) => {
  return fetch(
    `${endpoint}/congress/${session}/${chamber.toLowerCase()}-bill/${bill}/${version}/diffs/${uscTitle}/${uscSection}`
  )
    .then(res => res.json())
    .then(res => {
      let ret = {}
      lodash.forEach(res.diffs, obj => {
        ret[`${obj.usc_content_id}`] = obj;
      } );
      return ret;
    })
}