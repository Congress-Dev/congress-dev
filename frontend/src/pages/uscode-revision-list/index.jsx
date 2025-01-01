// Hold the different versions of the USCode we can look at
import React, { useEffect, useState } from "react";
import lodash from "lodash";
import { Section, SectionCard } from "@blueprintjs/core";

import { USCRevisionBox } from "components";
import { getUSCRevisions } from "common/api";

function USCodeRevisionList() {
    const [releases, setReleases] = useState([]);

    useEffect(() => {
        getUSCRevisions().then(setReleases);
    }, []);

    return (
        <Section
            className="page"
            title="United States Code"
            subtitle="The Foundation of U.S. Law"
        >
            <SectionCard>
                {lodash.map(
                    releases,
                    (
                        {
                            usc_release_id,
                            effective_date,
                            long_title,
                            short_title,
                            url,
                        },
                        ind,
                    ) => (
                        <USCRevisionBox
                            key={`usc-rev-box-${ind}`}
                            usc_release_id={usc_release_id}
                            effective_date={effective_date}
                            long_title={long_title}
                            short_title={short_title}
                            url={
                                "https://uscode.house.gov/download/releasepoints/us/pl/116/78/usc-rp@116-78.htm"
                            }
                        />
                    ),
                )}
            </SectionCard>
        </Section>
    );
}

export default USCodeRevisionList;
