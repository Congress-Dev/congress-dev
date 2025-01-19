import React, { useEffect, useState } from "react";
import { Tabs, Tab, NonIdealState, NonIdealStateIconSize } from "@blueprintjs/core";
import USCTrackingTab from "./usc-tracking-tab";
import { getUSCTrackingFolders } from "common/api";

export default function USCTrackingTabs() {
    const [folders, setFolders] = useState([]);
    const [selectedTab, setSelectedTab] = useState(null);

    useEffect(() => {
        getUSCTrackingFolders()
            .then((res) => res.json())
            .then((res) => {
                console.log(res);
                setFolders(res || []);
                if (res && res.length > 0) {
                    setSelectedTab(res[0].userUscContentFolderId);
                }
            });
    }, []);
    console.log(folders);
    return folders.length == 0 ? (
        <NonIdealState
            icon="inbox"
            iconSize={NonIdealStateIconSize.STANDARD}
            title="No legislation results for this week"
            description={
                <>
                    Try adding more legislation to favorites,
                    <br />
                    or check back later.
                </>
            }
            layout="vertical"
        />
    ) : (
        <Tabs
            id="usc-tracking-tabs"
            selectedTabId={selectedTab}
            onChange={(newTab) => setSelectedTab(newTab)}
        >
            {folders.map((folder) => (
                <Tab
                    key={folder.userUscContentFolderId}
                    id={folder.userUscContentFolderId}
                    title={folder.name}
                    panel={
                        <USCTrackingTab
                            folderId={folder.userUscContentFolderId}
                        />
                    }
                />
            ))}
        </Tabs>
    );
}
