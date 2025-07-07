import { Callout, HTMLTable, Tag } from "@blueprintjs/core";

function EffectiveDateItem({ action, onNavigate, contentLookup }) {
    const actions = action.actions?.[0] || {};
    const effectiveAction = actions["EFFECTIVE-DATE"];
    
    if (!effectiveAction) {
        return null;
    }

    const formatTimeframe = (amount, unit) => {
        if (amount === "0") {
            return "Immediately upon enactment";
        }
        const unitDisplay = amount === "1" ? unit.replace(/s$/, "") : unit;
        return `${amount} ${unitDisplay} after enactment`;
    };

    const getActionDescription = () => {
        if (effectiveAction.effective_date) {
            return `Takes effect on ${effectiveAction.effective_date}`;
        }
        if (effectiveAction.amount && effectiveAction.unit) {
            return formatTimeframe(effectiveAction.amount, effectiveAction.unit);
        }
        return "Takes effect as specified";
    };

    const getTargetDescription = () => {
        if (effectiveAction.target) {
            return effectiveAction.target;
        }
        return "General provision";
    };

    const getContentText = () => {
        if (!contentLookup || !action.legislationContentId) {
            return null;
        }
        return contentLookup[action.legislationContentId];
    };

    const contentText = getContentText();

    return (
        <>
            <Callout>
                <h4
                    className="effective-date-title"
                    onClick={() => onNavigate && onNavigate(action.legislation_content_id)}
                    style={{ cursor: "pointer" }}
                >
                    Effective Date Action{" "}
                    {effectiveAction.amount === "0" && (
                        <Tag intent="success" minimal>Immediate</Tag>
                    )}
                    {effectiveAction.sunset_date && (
                        <Tag intent="warning" minimal>Has Sunset</Tag>
                    )}
                </h4>
                <HTMLTable
                    compact={true}
                    striped={true}
                    className="effective-date-item"
                >
                    <tbody>
                        <tr>
                            <td>
                                <b>Applies To</b>
                            </td>
                            <td>{getTargetDescription()}</td>
                        </tr>
                        <tr>
                            <td>
                                <b>Effective Date</b>
                            </td>
                            <td>{getActionDescription()}</td>
                        </tr>
                        {effectiveAction.effective_date && (
                            <tr>
                                <td>
                                    <b>Specific Date</b>
                                </td>
                                <td>{effectiveAction.effective_date}</td>
                            </tr>
                        )}
                        {effectiveAction.sunset_date && (
                            <tr>
                                <td>
                                    <b>Sunset Date</b>
                                </td>
                                <td>{effectiveAction.sunset_date}</td>
                            </tr>
                        )}
                        {effectiveAction.trigger_date && (
                            <tr>
                                <td>
                                    <b>Trigger</b>
                                </td>
                                <td>{effectiveAction.trigger_date}</td>
                            </tr>
                        )}
                        {contentText && (
                            <tr>
                                <td>
                                    <b>Content</b>
                                </td>
                                <td style={{ fontStyle: "italic", maxWidth: "400px" }}>
                                    {contentText}
                                </td>
                            </tr>
                        )}
                    </tbody>
                </HTMLTable>
            </Callout>
            <br />
        </>
    );
}

export default EffectiveDateItem; 