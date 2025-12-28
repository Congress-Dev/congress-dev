import React, { createContext } from "react";

// Type definitions for the BillContext

export interface LegislationVersion {
    legislation_version_id: number;
    legislation_version: string;
    effective_date?: string;
    created_at?: string;
}

export interface LegislationAction {
    actionDate: string;
    text: string;
    sourceName: string;
    actionCode?: string;
    sourceCode?: string;
}

export interface LegislationVote {
    question: string;
    datetime: string;
    passed: boolean;
    // Add other vote properties as needed
}

export interface Sponsor {
    // Define sponsor properties based on your data structure
    [key: string]: any;
}

export interface Appropriation {
    appropriationId: number;
    parentId?: number;
    amount: number;
    fiscalYears: number[];
    untilExpended: boolean;
    newSpending: boolean;
    briefPurpose: string;
    expirationYear?: number;
    legislationContentId: number;
}

export interface Bill {
    legislation_id: number;
    title: string;
    congress: number;
    chamber: string;
    number: number;
    legislation_versions: LegislationVersion[];
    usc_release_id?: string | number;
    effective_date?: string;
}

export interface Bill2 {
    sponsor?: Sponsor;
    actions?: LegislationAction[];
    votes?: LegislationVote[];
    appropriations?: Appropriation[];
}

export interface BillSummary {
    summary: string;
    // Add other summary properties as needed
}

export interface TextTreeNode {
    legislation_content_id: number;
    lc_ident?: string;
    content_str?: string;
    section_display?: string;
    heading?: string;
    content_type?: string;
    children?: TextTreeNode[];
}

export interface TextTree extends TextTreeNode {
    loading?: boolean;
}

export interface DateAnchor {
    title: string;
    hash: string;
}

export interface BillContextValue {
    // Core bill data
    bill: Bill;
    bill2: Bill2;
    billEffective: string | null;
    billNumber: number;
    billSummary: BillSummary[];
    billVers: string;
    billVersion: string;
    billVersionId: number;
    
    // URL/routing data
    chamber: string;
    congress: number;
    
    // Content structure
    textTree: TextTree;
    dateAnchors: DateAnchor[];
    
    // Functions
    scrollContentIdIntoView: (contentId: number) => void;
    setBillVers: (version: string) => void;
}

// Create context with proper typing
export const BillContext = createContext<BillContextValue | undefined>(undefined);

// Custom hook for using BillContext with type safety
export const useBillContext = (): BillContextValue => {
    const context = React.useContext(BillContext);
    if (context === undefined) {
        throw new Error('useBillContext must be used within a BillContext.Provider');
    }
    return context;
}; 