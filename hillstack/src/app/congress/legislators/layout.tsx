'use client';

import type { legislationchamber } from 'generated/prisma/enums';
import type { LegislatorScalarFieldEnum } from 'generated/prisma/internal/prismaNamespace';
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

const SORT: ToolbarFilterOption<
	ToolbarFilterSortMap<LegislatorScalarFieldEnum>
>[] = [
	{ value: { first_name: 'asc' }, label: 'First Name (A-Z)' },
	{ value: { first_name: 'desc' }, label: 'First Name (Z-A)' },
	{ value: { last_name: 'asc' }, label: 'Last Name (A-Z)' },
	{ value: { last_name: 'desc' }, label: 'Last Name (Z-A)' },
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
};

export type FilterConfigType = typeof filterConfig;

export default function LegislatorSearchLayout({
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
