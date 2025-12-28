'use client';

import type { legislationchamber } from 'generated/prisma/enums';
import type { Legislation_committeeScalarFieldEnum } from 'generated/prisma/internal/prismaNamespace';
import { OmniSearchProvider } from '~/contexts';
import type {
	ToolbarFilterOption,
	ToolbarFilterSortMap,
} from '~/types/components';

const SESSIONS: ToolbarFilterOption<number>[] = [
	{ value: 117, label: '117th' },
	{ value: 118, label: '118th' },
	{ value: 119, label: '119th' },
];

const CHAMBERS: ToolbarFilterOption<legislationchamber>[] = [
	{ value: 'House', label: 'House' },
	{ value: 'Senate', label: 'Senate' },
];

// const TYPES: ToolbarFilterOption<string>[] = [
// 	{ value: 'Standing', label: 'Standing' },
// 	{ value: 'Joint', label: 'Joint' },
// 	{ value: 'Select', label: 'Select' },
// 	{ value: 'Special', label: 'Special' },
// ];

const SORT: ToolbarFilterOption<
	ToolbarFilterSortMap<Legislation_committeeScalarFieldEnum>
>[] = [
	{ value: { name: 'asc' }, label: 'Name (A-Z)' },
	{ value: { name: 'desc' }, label: 'Name (Z-A)' },
];

const filterConfig = {
	congress: {
		title: 'Session',
		options: SESSIONS,
		multiSelect: true as const,
	},
	chamber: {
		title: 'Chamber',
		options: CHAMBERS,
		multiSelect: true as const,
	},
	sort: {
		title: 'Sort',
		options: SORT,
		multiSelect: false as const,
		searchable: false,
	},
	// committeeType: {
	// 	title: 'Type',
	// 	options: TYPES,
	// 	multiSelect: true as const,
	// },
};

export type FilterConfigType = typeof filterConfig;

export default function CommitteesSearchLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<OmniSearchProvider filterConfig={filterConfig}>
			{children}
		</OmniSearchProvider>
	);
}
