import lodash from "lodash";

import { toastError } from "./utils";

function handleStatus(res) {
    if (res.status === 200) {
        return res.json();
    } else {
        console.error(res);
        throw new Error(res);
        return null;
    }
}
export const capFirstLetter = function (str) {
    return str.charAt(0).toUpperCase() + str.substring(1);
};

let endP = process.env.REACT_APP_API_URL || "http://localhost:9090";
let endPv2 = process.env.REACT_APP_API_V2_URL || "http://localhost:9091";
if (window.location.href.includes("congress.dev")) {
    endP = "https://api.congress.dev";
    endPv2 = "https://api-v2.congress.dev";
}
export const endpoint = endP;

export const getBill = (congress, chamber, billNumber) => {
    return fetch(
        `${endpoint}/congress/${congress}/${capFirstLetter(
            chamber,
        )}-bill/${billNumber}`,
    )
        .then(handleStatus)
        .catch(toastError);
};

export const getBill2 = (legislationId, versionStr) => {
    return fetch(`${endPv2}/legislation/${legislationId}/${versionStr}`)
        .then(handleStatus)
        .catch(toastError);
};

export const getBillSummary = (legislationVersionId) => {
    return fetch(
        `${endPv2}/legislation_version/${legislationVersionId}/summaries`,
    )
        .then(handleStatus)
        .catch(() => {});
};

export const getBillVersionText = (
    congress,
    chamber,
    billNumber,
    billVersion,
) => {
    // Grab the bill text, and then put it into the nested format
    // TODO: Move this treeification to the server?
    return fetch(
        `${endpoint}/congress/${congress}/${chamber.toLowerCase()}-bill/${billNumber}/${billVersion}/text?include_parsed=true`,
    )
        .then(handleStatus)
        .then((flatJson) => {
            if (flatJson) {
                let looped = {};
                const sorted = lodash.sortBy(
                    flatJson.content,
                    ({ legislation_content_id, order_number }) =>
                        `${legislation_content_id
                            .toString()
                            .padStart(
                                10,
                                "0",
                            )}.${order_number.toString().padStart(3, "0")}`,
                );
                if (sorted.length === 0) {
                    return {};
                }
                lodash.forEach(sorted, (obj) => {
                    let copyObj = { ...obj, children: [] };
                    looped[copyObj.legislation_content_id] = copyObj;
                    if (copyObj.parent_id) {
                        looped[copyObj.parent_id].children.push(copyObj);
                    }
                });
                return looped[sorted[0].legislation_content_id];
            } else {
                return {};
            }
        })
        .catch(toastError);
};

export const getUSCRevisions = () => {
    // Grab the list of USCode revision points from the server
    return fetch(`${endpoint}/usc/releases`)
        .then(handleStatus)
        .then((obj) => obj.releases)
        .catch(toastError);
};

export const getUSCTitleList = (uscReleaseId) => {
    return fetch(`${endpoint}/usc/${uscReleaseId}/titles`)
        .then(handleStatus)
        .then(({ titles }) => lodash.sortBy(titles, "short_title"))
        .catch(toastError);
};

export const getUSCSectionList = (uscReleaseId, shortTitle) => {
    return fetch(`${endpoint}/usc/${uscReleaseId}/${shortTitle}/sections`)
        .then(handleStatus)
        .then(({ sections }) => lodash.sortBy(sections, "number"))
        .catch(toastError);
};

export const getUSCLevelSections = (
    uscReleaseId,
    shortTitle,
    uscSectionId = null,
) => {
    let url = `${endpoint}/usc/${uscReleaseId}/${shortTitle}/levels`;
    if (uscSectionId) {
        url = `${endpoint}/usc/${uscReleaseId}/${shortTitle}/levels/${uscSectionId}`;
    }
    return fetch(url)
        .then(handleStatus)
        .then(({ sections }) => lodash.sortBy(sections, "usc_section_id"))
        .catch(toastError);
};

export const getUSCSectionLineage = (
    uscReleaseId,
    shortTitle,
    uscSectionId,
) => {
    return fetch(
        `${endpoint}/usc/${uscReleaseId}/${shortTitle}/lineage/${uscSectionId}`,
    )
        .then(handleStatus)
        .then(({ sections }) => lodash.sortBy(sections, "usc_section_id"))
        .catch(toastError);
};

export const getUSCSectionContent = (
    uscReleaseId,
    shortTitle,
    sectionNumber,
) => {
    return fetch(
        `${endpoint}/usc/${uscReleaseId}/${shortTitle}/${sectionNumber}/text`,
    )
        .then(handleStatus)
        .then((flatJson) => {
            if (flatJson) {
                let looped = {};
                const sorted = lodash.sortBy(
                    flatJson.content,
                    ({ usc_content_id, order_number }) =>
                        `${usc_content_id}.${order_number.toString().padStart(3, "0")}`,
                );
                if (sorted.length === 0) {
                    return {};
                }
                lodash.forEach(sorted, (obj) => {
                    let copyObj = { ...obj, children: [] };
                    looped[copyObj.usc_content_id] = copyObj;
                    if (copyObj.parent_id) {
                        looped[copyObj.parent_id].children.push(copyObj);
                    }
                });
                return { children: [looped[sorted[0].usc_content_id]] };
            } else {
                return {};
            }
        })
        .catch(toastError);
};

export const getCongressSearch = (
    congress,
    chamber,
    versions,
    text,
    sort,
    page,
    pageSize,
) => {
    return fetch(
        `${endPv2}/legislation/search?congress=${congress || "None"}&chamber=${
            chamber || "None"
        }&versions=${versions || ""}&text=${text}&sort=${sort}&page=${page}&pageSize=${pageSize}`,
    )
        .then(handleStatus)
        .catch(toastError);
};

export const getBillVersionDiffSummary = (session, chamber, bill, version) => {
    return fetch(
        `${endpoint}/congress/${session}/${chamber.toLowerCase()}-bill/${bill}/${version}/diffs`,
    )
        .then(handleStatus)
        .catch(toastError);
};

export const getBillVersionDiffForSection = (
    session,
    chamber,
    bill,
    version,
    uscTitle,
    uscSection,
) => {
    return fetch(
        `${endpoint}/congress/${session}/${chamber.toLowerCase()}-bill/${bill}/${version}/diffs/${uscTitle}/${uscSection}`,
    )
        .then(handleStatus)
        .then((res) => {
            if (res) {
                let ret = {};
                lodash.forEach(res.diffs, (obj) => {
                    ret[`${obj.usc_content_id}`] = obj;
                });
                return ret;
            } else {
                return {};
            }
        })
        .catch(toastError);
};

// Endpoint V2 being

export const getMemberInfo = (bioGuideId) => {
    return fetch(`${endPv2}/member/${bioGuideId}`)
        .then(handleStatus)
        .catch(toastError);
};

export const getMemberSponsoredLegislation = (bioGuideId) => {
    return fetch(`${endPv2}/member/${bioGuideId}/sponsorships`)
        .then(handleStatus)
        .catch(toastError);
};
