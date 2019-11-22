import { host } from './utils';

const titlesKey = 'titles';
const titleKeyPrefix = 'title_';
const sectionKeyPrefix = 'section_';
const versionKeyPrefix = 'version_';
const billKeyPrefix = 'bill_';
const revisionDiffPrefix = 'revisionDiff_';


const storage = window.sessionStorage || {
    getItem: () => null,
    setItem: () => null
};
const storeValue = function (key, value) {
    try {
        storage.setItem(key, value);
    } catch (e) {
        console.log('Error while setting storage');
    }
}
export const getTitles = function getTitles() {
    return new Promise((resolve, reject) => {
        const res = JSON.parse(storage.getItem(titlesKey));
        if (res) {
            console.log('Retrieved titles from localStorage');
            resolve(res);
        } else {
            fetch(`${host}/titles`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    storeValue(titlesKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};

export const getTitleContent = function getTitleContent(titleId) {
    return new Promise((resolve, reject) => {
        const titleKey = `${titleKeyPrefix}${titleId}`;
        const res = JSON.parse(storage.getItem(titleKey));
        if (res) {
            console.log(`Retrieved title ${titleId} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/latest/chapter/${titleId}`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(titleKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};

export const getSectionContent = function getSectionContent(titleId, sectionId) {
    return new Promise((resolve, reject) => {
        const sectionKey = `${sectionKeyPrefix}${titleId}_${sectionId}`;
        const res = JSON.parse(storage.getItem(sectionKey));
        if (res) {
            console.log(`Retrieved section ${titleId}-${sectionId} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/latest/section/${titleId}/${sectionId}`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(sectionKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};

export const getVersionContent = function getVersionContent(version) {
    return new Promise((resolve, reject) => {
        const versionKey = `${versionKeyPrefix}${version}`;
        const res = JSON.parse(storage.getItem(versionKey));
        if (res) {
            console.log(`Retrieved version ${version} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/version`,
                {
                    method: 'post',
                    body: JSON.stringify({ version }),
                    headers: { 'Content-Type': 'application/json' }
                })
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(versionKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};

export const getBillContent = function getBillContent(billId) {
    return new Promise((resolve, reject) => {
        const billKey = `${billKeyPrefix}${billId}`;
        const res = JSON.parse(storage.getItem(billKey));
        if (res) {
            console.log(`Retrieved bill ${billId} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/bill/${billId}`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(billKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};

export const getBillContent2 = function getBillContent2(billId) {
    return new Promise((resolve, reject) => {
        const billKey = `${billKeyPrefix}tree_${billId}`;
        const res = JSON.parse(storage.getItem(billKey));
        if (res) {
            console.log(`Retrieved bill_tree ${billId} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/bill_tree/${billId}`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(billKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};


export const getRevisionDiff = function getRevisionDiff(baseId, compareId) {
    return new Promise((resolve, reject) => {
        const diffKey = `${revisionDiffPrefix}_${baseId}_${compareId}`;
        const res = JSON.parse(storage.getItem(diffKey));
        if (res) {
            console.log(`Retrieved revision comparison ${diffKey} from localStorage`);
            resolve(res);
        } else {
            fetch(`${host}/rev_diff/${baseId}/${compareId}`)
                .then((resp) => resp.json())
                .then((jsResp) => {
                    // console.log('Storing to LS');
                    storeValue(diffKey, JSON.stringify(jsResp));
                    resolve(jsResp);
                });
        }
    });
};