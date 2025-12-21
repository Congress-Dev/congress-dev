'use client';

import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type * as React from 'react';
import { congressTabs } from '~/constants';

export default function CongressLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	const pathname = usePathname();
	const pathParts = pathname.split('/');
	const activePath = `/${pathParts[1]}/${pathParts[2]}`;

	return (
		<Box sx={{ width: '100%' }}>
			<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
				<Tabs
					allowScrollButtonsMobile
					scrollButtons={false}
					value={congressTabs[activePath]?.id ?? 0}
					variant='scrollable'
				>
					{Object.keys(congressTabs).map((href, idx) => {
						const { label, icon } = congressTabs[href] ?? {};

						return (
							<Tab
								component={Link}
								href={href}
								icon={icon}
								iconPosition='start'
								key={href}
								label={label}
								sx={{ px: idx ? 2 : 0, minWidth: 50 }}
							/>
						);
					})}
				</Tabs>
			</Box>
			<Container maxWidth='xl' sx={{ px: { xs: 0 } }}>
				<Box sx={{ pt: 3 }}>{children}</Box>
			</Container>
		</Box>
	);
}
