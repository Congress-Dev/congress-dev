import React, { useContext, useEffect, useState } from "react";
import { Spinner } from "@blueprintjs/core";

import { EffectiveDateItem } from "components";
import { BillContext } from "context";
import { getBillActionsv2 } from "common/api";

const EffectiveDateActions = () => {
    const { billVersionId, scrollContentIdIntoView, textTree } = useContext(BillContext);
    const [effectiveDateActions, setEffectiveDateActions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [contentLookup, setContentLookup] = useState({});

    // Create a lookup map from legislation_content_id to content_str
    useEffect(() => {
        if (!textTree || !textTree.children) {
            return;
        }

        const lookup = {};
        
        const buildLookup = (node) => {
            if (node.legislation_content_id && node.content_str) {
                lookup[node.legislation_content_id] = node.content_str;
            }
            
            if (node.children) {
                node.children.forEach(buildLookup);
            }
        };

        buildLookup(textTree);
        setContentLookup(lookup);
        console.log(lookup);
    }, [textTree]);

    useEffect(() => {
        if (!billVersionId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        setError(null);
        
        getBillActionsv2(billVersionId)
            .then((actions) => {
                if (!actions || !Array.isArray(actions)) {
                    setEffectiveDateActions([]);
                    setLoading(false);
                    return;
                }

                // Filter actions to only include those with EFFECTIVE-DATE actions
                const effectiveActions = actions.filter(action => {
                    const actionData = action.actions?.[0];
                    return actionData && actionData["EFFECTIVE-DATE"];
                });
                
                setEffectiveDateActions(effectiveActions);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Error fetching effective date actions:", err);
                setError(err);
                setLoading(false);
            });
    }, [billVersionId]);

    if (loading) {
        return <Spinner className="loading-spinner" intent="primary" />;
    }

    if (error) {
        return (
            <p>
                Error loading effective date actions. Please try again later.
            </p>
        );
    }

    if (!billVersionId) {
        return (
            <p>
                Bill version information is not available.
            </p>
        );
    }

    return effectiveDateActions.length > 0 ? (
        <>
            {effectiveDateActions.map((action) => (
                <EffectiveDateItem
                    key={action.legislation_action_parse_id}
                    action={action}
                    onNavigate={scrollContentIdIntoView}
                    contentLookup={contentLookup}
                />
            ))}
        </>
    ) : (
        <p>
            There are no effective date actions parsed in the contents of this
            bill.
        </p>
    );
};

export default EffectiveDateActions; 