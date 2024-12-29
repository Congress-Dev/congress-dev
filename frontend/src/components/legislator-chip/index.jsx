import { CompoundTag } from "@blueprintjs/core";

import { partyLookup } from "common/lookups";

function LegislatorChip({ bill }) {
    return bill.sponsor != null ? (
        <>
            <span style={{ fontWeight: "bold" }}>Sponsor:</span>{" "}
            <CompoundTag
                intent={
                    bill.sponsor.party == "Republican"
                        ? "danger"
                        : bill.sponsor.party == "Democrat"
                          ? "primary"
                          : "none"
                }
                leftContent={
                    partyLookup[bill.sponsor.party] != null
                        ? partyLookup[bill.sponsor.party]
                        : bill.sponsor.party
                }
            >
                &nbsp;{bill.sponsor.lastName}, {bill.sponsor.firstName}&nbsp;
            </CompoundTag>
            <br />
        </>
    ) : (
        <></>
    );
}

export default LegislatorChip;
