'use client';

import { Card, Grid, Toolbar } from '@mui/material';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import type React from 'react';
import { LegislationCalendar } from '~/app/_home/widgets/legislationCalendar';
import { LegislationTags } from '~/app/_home/widgets/legislationTags';

function DashboardWidget({
	title,
	children,
}: {
	title: string;
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
				{title}
			</Toolbar>
			<Box sx={{ px: 3, pt: 1, pb: 2, minHeight: 200 }}>{children}</Box>
		</Card>
	);
}

export function Dashboard() {
	return (
		<Box sx={{ minWidth: '100%' }}>
			<Grid container spacing={2} sx={{ mt: 2 }}>
				<Grid size={4}>
					<DashboardWidget title='Top Legislation Tags'>
						<LegislationTags />
					</DashboardWidget>
				</Grid>
				<Grid size={8}>
					<DashboardWidget title='Legislation Calendar'>
						<LegislationCalendar />
					</DashboardWidget>
				</Grid>
				<Grid size={6}>
					<DashboardWidget title='Followed Legislation'></DashboardWidget>
				</Grid>
				<Grid size={6}>
					<DashboardWidget title='Followed Legislators'></DashboardWidget>
				</Grid>
				<Grid size={12}>
					<DashboardWidget title='USC Tracking'></DashboardWidget>
				</Grid>
			</Grid>
		</Box>
	);
}
