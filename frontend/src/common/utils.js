import { Position, Intent, OverlayToaster } from "@blueprintjs/core";

export const toastError = (e) => {
    const myToaster = OverlayToaster.create({ position: Position.TOP });
    console.error(e);
    myToaster.show({
        intent: Intent.DANGER,
        icon: "warning-sign",
        message: `Something went wrong!`,
    });
};

export const getLongestString = (str1, str2) => {
    if (str1.length > str2.length) {
        return str1;
    }
    return str2;
};
