import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Link from 'next/link';
import { HomePage } from '~/app/_home/page';
import { navigationLinks } from '~/constants';

export default async function Home() {
	return (
		<Box sx={{ width: '100%' }}>
			<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
				<Tabs
					allowScrollButtonsMobile
					scrollButtons={false}
					value={0}
					variant='scrollable'
				>
					{navigationLinks.map((page) => {
						const { label, href } = page;
						return (
							<Tab
								component={Link}
								href={href}
								icon={<page.icon />}
								iconPosition='start'
								key={href}
								label={label}
								sx={{ px: 2, minWidth: 50 }}
							/>
						);
					})}
				</Tabs>
			</Box>
			<Container maxWidth='xl' sx={{ pt: 3 }}>
				<Paper elevation={1} sx={{ p: 3 }}>
					<HomePage />
				</Paper>
			</Container>
		</Box>
	);
}
