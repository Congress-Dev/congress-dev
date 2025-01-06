export const chamberLookup = {
    [undefined]: "",
    House: "H.R.",
    Senate: "S.",
};

export const versionSort = {
    ih: 1,
    is: 1,
    rfh: 2,
    rfs: 2,
    rds: 3,
    rhs: 3,
    rcs: 4,
    rch: 4,
    rs: 5,
    rh: 5,
    pcs: 6,
    pch: 6,
    cps: 7,
    cph: 7,
    eas: 8,
    eah: 8,
    es: 9,
    eh: 9,
    ras: 10,
    rah: 10,
    enr: 11,
};

export const versionToFull = {
    ih: "Introduced",
    is: "Introduced",
    rfh: "Referred",
    rfs: "Referred",
    rds: "Received",
    rhs: "Received",
    rcs: "Reference Change",
    rch: "Reference Change",
    rs: "Reported",
    rh: "Reported",
    pcs: "Placed on Calendar",
    pch: "Placed on Calendar",
    cps: "Considered and Passed",
    cph: "Considered and Passed",
    eas: "Engrossed Amendment",
    eah: "Engrossed Amendment",
    es: "Engrossed",
    eh: "Engrossed",
    ras: "Referred w/Amendments",
    rah: "Referred w/Amendments",
    enr: "Enrolled",
};

export const initialVersionToFull = {
    Introduced: true,
    Referred: true,
    Received: true,
    "Reference Change": true,
    Reported: true,
    "Placed on Calendar": true,
    "Considered and Passed": true,
    "Engrossed Amendment": true,
    Engrossed: true,
    "Referred w/Amendments": true,
    Enrolled: true,
};

export const partyLookup = {
    "Republican": "R",
    "Democrat": "D",
    "Independent": "I",
}

export const partyIntent = {
    "Republican": "danger",
    "Democrat": "primary",
    "Independent": "warning",
}