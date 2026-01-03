'use client';

import { styled, Tab, Tabs } from '@mui/material';
import Link from 'next/link';
import { useParams, usePathname } from 'next/navigation';
import { congressBillTabs } from '~/constants';

const PageTabs = styled(Tabs)(({ theme }) => ({
	marginTop: theme.spacing(3),
	paddingBottom: theme.spacing(1),
	minHeight: 0,

	overflow: 'visible',

	'& .MuiTab-root': {
		padding: theme.spacing(0.5),
		paddingLeft: theme.spacing(1.5),
		paddingRight: theme.spacing(1.5),
	},
	'& .Mui-selected': {
		border: `1px solid ${theme.palette.divider}`,
		borderRadius: '4px',
	},
	'& .MuiTabs-indicator': {
		bottom: '-2px',
		transition: 'none !important',
		backgroundColor: 'transparent',
	},
	'& .MuiTouchRipple-root': {
		borderRadius: '4px 4px 0 0',
	},
	'& .MuiTabs-indicator::after': {
		content: '""',
		background: theme.palette.background.default,
		width: 'calc(100% - 2px)',
		display: 'block',
		marginLeft: '1px',
		height: '1px',
	},

	[theme.breakpoints.up('md')]: {
		paddingBottom: 0,
		borderBottom: `1px solid ${theme.palette.divider}`,
		'& .MuiTabs-scroller': {
			overflow: 'visible !important',
		},
		'& .Mui-selected': {
			borderBottom: 'none',
			borderRadius: '4px 4px 0 0',
		},
	},
}));

export function BillTabs() {
	const params = useParams();
	const tabs = congressBillTabs({ params });
	const pathname = usePathname();

	return (
		<PageTabs
			allowScrollButtonsMobile
			scrollButtons={false}
			slotProps={{}}
			value={tabs[pathname]?.id ?? 0}
			variant='scrollable'
		>
			{Object.keys(tabs).map((href) => {
				const { label, icon } = tabs[href] ?? {};

				return (
					<Tab
						component={Link}
						href={href}
						icon={icon}
						iconPosition='start'
						key={href}
						label={label}
					/>
				);
			})}
		</PageTabs>
	);
}
