import { Position, Intent, OverlayToaster } from "@blueprintjs/core";

export const toastError = (e) => {
    const myToaster = OverlayToaster.create({ position: Position.TOP });
    myToaster.show({
        intent: Intent.DANGER,
        icon: "warning-sign",
        message: `Something went wrong!`,
    });
};
