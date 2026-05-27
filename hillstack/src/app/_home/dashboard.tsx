'use client';

import type { SvgIconComponent } from '@mui/icons-material';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import GavelIcon from '@mui/icons-material/Gavel';
import HistoryEduIcon from '@mui/icons-material/HistoryEdu';
import LocalPoliceIcon from '@mui/icons-material/LocalPolice';
import SellIcon from '@mui/icons-material/Sell';
import { Card, Grid, Toolbar } from '@mui/material';
import Box from '@mui/material/Box';
import type React from 'react';
import { InterestFeed } from '~/app/_home/widgets/interestFeed';
import { LegislationCalendar } from '~/app/_home/widgets/legislationCalendar';
import { LegislationFollowed } from '~/app/_home/widgets/legislationFollowed';
import { LegislationTags } from '~/app/_home/widgets/legislationTags';
import { LegislatorFollowed } from '~/app/_home/widgets/legislatorFollowed';

function DashboardWidget({
	title,
	Icon,
	children,
}: {
	title: string;
	Icon?: SvgIconComponent;
	children?: React.ReactNode;
}) {
	return (
		<Card elevation={2}>
			<Toolbar
				disableGutters
				sx={{
					height: '40px',
					minHeight: '40px',
					px: 2,
				}}
				variant='dense'
			>
				{Icon && <Icon sx={{ mr: 1, fontSize: '18px' }} />}
				{title}
			</Toolbar>
			<Box sx={{ minHeight: 230 }}>{children}</Box>
		</Card>
	);
}

export function Dashboard() {
	return (
		<Box sx={{ minWidth: '100%' }}>
			<Grid container spacing={2} sx={{ mt: 2 }}>
				<Grid size={{ xs: 12, md: 4 }}>
					<DashboardWidget
						Icon={SellIcon}
						title='Top Legislation Tags'
					>
						<LegislationTags />
					</DashboardWidget>
				</Grid>
				<Grid size={{ xs: 12, md: 8 }}>
					<DashboardWidget
						Icon={CalendarMonthIcon}
						title='Legislation Calendar'
					>
						<LegislationCalendar />
					</DashboardWidget>
				</Grid>
				<Grid size={{ xs: 12, md: 6 }}>
					<DashboardWidget
						Icon={HistoryEduIcon}
						title='Followed Legislation'
					>
						<LegislationFollowed />
					</DashboardWidget>
				</Grid>
				<Grid size={{ xs: 12, md: 6 }}>
					<DashboardWidget
						Icon={GavelIcon}
						title='Followed Legislators'
					>
						<LegislatorFollowed />
					</DashboardWidget>
				</Grid>
				<Grid size={{ xs: 12, md: 12 }}>
					<DashboardWidget
						Icon={LocalPoliceIcon}
						title='Your Interest Areas'
					>
						<InterestFeed />
					</DashboardWidget>
				</Grid>
			</Grid>
		</Box>
	);
}
