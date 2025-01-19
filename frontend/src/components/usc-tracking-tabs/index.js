import React, { useEffect, useState } from "react";
import { Tabs, Tab } from "@blueprintjs/core";
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
    return (
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
