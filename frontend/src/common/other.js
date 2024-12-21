import crypto from "crypto-browserify";

export const md5 = function (str) {
    // Take a string and run it through the MD5 function
    return crypto.createHash("md5").update(str).digest("hex");
};
