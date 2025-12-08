'use client';

import type { legislationchamber } from 'generated/prisma/enums';
import { OmniSearchProvider } from '~/contexts';
import type { ToolbarFilterOption } from '~/types/components';

const SESSIONS: ToolbarFilterOption<string>[] = [
	{ value: '117', label: '117th' },
	{ value: '118', label: '118th' },
	{ value: '119', label: '119th' },
];

const CHAMBERS: ToolbarFilterOption<legislationchamber>[] = [
	{ value: 'House', label: 'House' },
	{ value: 'Senate', label: 'Senate' },
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
