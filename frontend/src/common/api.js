import lodash from "lodash";

import { toastError } from "./utils";

function handleStatus(res) {
    if (res.status === 200) {
        return res.json();
    } else {
        console.error(res);
        const err = new Error(res);
        err.name = "HTTP Error: " + res.status;
        throw err;
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

export const userGet = () => {
    return fetch(`${endPv2}/user`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userLogin = (accessToken, expiresIn) => {
    return fetch(`${endPv2}/user/login`, {
        method: "POST",
        body: JSON.stringify({
            access_token: accessToken,
            expires_in: expiresIn,
        }),
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userLogout = () => {
    return fetch(`${endPv2}/user/logout`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetLegislation = () => {
    return fetch(`${endPv2}/user/legislation`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetLegislator = () => {
    return fetch(`${endPv2}/user/legislator`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetLegislationFeed = () => {
    return fetch(`${endPv2}/user/legislation/feed`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetLegislatorFeed = () => {
    return fetch(`${endPv2}/user/legislator/feed`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetStats = () => {
    return fetch(`${endPv2}/user/stats`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userGetFolders = () => {
    return fetch(`${endPv2}/user/usc_tracking/folders`, {
        credentials: "include",
    })
        .then(handleStatus)
        .catch(toastError);
};

export const userAddLegislation = (legislationId) => {
    return fetch(
        `${endPv2}/user/legislation/update?action=add&legislation_id=${legislationId}`,
        {
            credentials: "include",
        },
    )
        .then(handleStatus)
        .catch(toastError);
};

export const userRemoveLegislation = (legislationId) => {
    return fetch(
        `${endPv2}/user/legislation/update?action=remove&legislation_id=${legislationId}`,
        {
            credentials: "include",
        },
    )
        .then(handleStatus)
        .catch(toastError);
};

export const userAddLegislator = (bioGuideId) => {
    return fetch(
        `${endPv2}/user/legislator/update?action=add&bioguide_id=${bioGuideId}`,
        {
            credentials: "include",
        },
    )
        .then(handleStatus)
        .catch(toastError);
};
export const getUSCTrackingFolders = () => {
    return fetch(`${endPv2}/user/usc_tracking/folders`, {
        credentials: "include",
    });
};

export const getUSCTrackingBills = (folderId) => {
    return fetch(`${endPv2}/user/usc_tracking/folder/${folderId}`, {
        credentials: "include",
    });
};
export const userRemoveLegislator = (bioGuideId) => {
    return fetch(
        `${endPv2}/user/legislator/update?action=remove&bioguide_id=${bioGuideId}`,
        {
            credentials: "include",
        },
    )
        .then(handleStatus)
        .catch(toastError);
};

export const statsGetLegislationCalendar = () => {
    return fetch(`${endPv2}/stats/legislation_calendar`)
        .then(handleStatus)
        .catch(toastError)
}

export const statsGetLegislationFunnel = () => {
    return fetch(`${endPv2}/stats/legislation_funnel`)
        .then(handleStatus)
        .catch(toastError)
}

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

export const getBillVersionTextv2 = (legislationVersionId) => {
    // Grab the bill text, and then put it into the nested format
    // TODO: Move this treeification to the server?
    return fetch(
        `${endPv2}/legislation_version/${legislationVersionId}/text?include_parsed=true`,
    )
        .then(handleStatus)
        .then((flatJson) => {
            if (flatJson) {
                let looped = {};
                const sorted = lodash.sortBy(
                    flatJson,
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
                // Create a fake root
                let looped = {
                    [null]: {
                        content_type: "{}section",
                        usc_content_id: 0,
                        usc_ident: "/",
                        children: [],
                    },
                };
                const sorted = lodash.sortBy(
                    flatJson.content,
                    ({ usc_content_id, order_number }) => usc_content_id,
                );
                if (sorted.length === 0) {
                    return {};
                }
                lodash.forEach(sorted, (obj) => {
                    let copyObj = { ...obj, children: [] };
                    looped[copyObj.usc_content_id] = copyObj;
                    if (copyObj.parent_id && looped[copyObj.parent_id]) {
                        looped[copyObj.parent_id].children.push(copyObj);
                    } else {
                        // If we can't find it, add it to the root
                        looped[null].children.push(copyObj);
                    }
                });
                return { children: [looped[null]] };
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
    direction,
    page,
    pageSize,
) => {
    return fetch(
        `${endPv2}/legislation/search?${congress != "" ? `congress=${congress}` : ""}&chamber=${
            chamber || "None"
        }&versions=${versions || ""}&text=${text}&sort=${sort}&direction=${direction}&page=${page}&pageSize=${pageSize}`,
    )
        .then(handleStatus)
        .catch(toastError);
};
export const getBillActionsv2 = (legislationVersionId) => {
    return fetch(
        `${endPv2}/legislation_version/${legislationVersionId}/actions`,
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
export const getMemberSearch = (
    name,
    party,
    state,
    congress,
    chamber,
    sort,
    direction,
    page,
    pageSize,
) => {
    return fetch(
        `${endPv2}/members?name=${name || ""}&congress=${congress?.join('&congress=') || ""}&chamber=${chamber?.join('&chamber=') || ""}&party=${party?.join("&party=") || ""}&state=${state?.join("&state=") || ""}&sort=${sort}&direction=${direction}&page=${page}&pageSize=${pageSize}`,
    )
        .then(handleStatus)
        .catch(toastError);
}

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

export const talkToBill = (legislationVersionId, query) => {
    return fetch(`${endPv2}/legislation_version/${legislationVersionId}/llm`, {
        method: "POST",
        body: JSON.stringify({ query }),
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
    })
        .then(handleStatus)
        // .catch(toastError);
}