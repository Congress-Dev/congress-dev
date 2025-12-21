'use client';

import type { legislationchamber } from 'generated/prisma/enums';
import { OmniSearchProvider } from '~/contexts';
import type { ToolbarFilterOption } from '~/types/components';

// const AUTHORS: ToolbarFilterOption<string>[] = [
// 	{ value: '0', label: 'Alma Adams' },
// 	{ value: '1', label: 'Mark Alford' },
// 	{ value: '2', label: 'Peter Aguilar' },
// 	{ value: '3', label: 'Rick Allen' },
// 	{ value: '4', label: 'Robert Aderholt' },
// ];

const SESSIONS: ToolbarFilterOption<number>[] = [
	{ value: 117, label: '117th' },
	{ value: 118, label: '118th' },
	{ value: 119, label: '119th' },
];

// const STATUSES: ToolbarFilterOption<string>[] = [
// 	{ value: 'Introduced', label: 'Introduced' },
// 	{ value: 'Referred', label: 'Referred' },
// 	{ value: 'Received', label: 'Received' },
// 	{ value: 'Reference Change', label: 'Reference Change' },
// 	{ value: 'Reported', label: 'Reported' },
// 	{ value: 'Placed on Calendar', label: 'Placed on Calendar' },
// 	{ value: 'Considered and Passed', label: 'Considered and Passed' },
// 	{ value: 'Engrossed Amendment', label: 'Engrossed Amendment' },
// 	{ value: 'Engrossed', label: 'Engrossed' },
// 	{ value: 'Referred w/Amendments', label: 'Referred w/Amendments' },
// 	{ value: 'Enrolled', label: 'Enrolled' },
// ];

const CHAMBERS: ToolbarFilterOption<legislationchamber>[] = [
	{ value: 'House', label: 'House' },
	{ value: 'Senate', label: 'Senate' },
];

const filterConfig = {
	// author: {
	// 	title: 'Author',
	// 	options: AUTHORS,
	// 	multiSelect: false as const,
	// },
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
	// version: {
	// 	title: 'Status',
	// 	options: STATUSES,
	// 	multiSelect: true as const,
	// },
};

export type FilterConfigType = typeof filterConfig;

export default function BillSearchLayout({
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
