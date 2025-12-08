'use client';

import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Link from 'next/link';
import { useParams, usePathname } from 'next/navigation';
import type * as React from 'react';
import { congressBillTabs, congressTabs } from '~/constants';

export default function CongressLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	const params = useParams();
	const pathname = usePathname();
	let tabs = congressTabs;

	if (pathname.match(/\/congress\/bills\/\d/)) {
		tabs = congressBillTabs({ params });
	}

	return (
		<Box sx={{ width: '100%' }}>
			<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
				<Tabs allowScrollButtonsMobile value={tabs[pathname]?.id ?? 0}>
					{Object.keys(tabs).map((href, idx) => {
						const { label, icon } = tabs[href] ?? {};

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
			<Container maxWidth='xl'>
				<Box sx={{ pt: 3 }}>{children}</Box>
			</Container>
		</Box>
	);
}
