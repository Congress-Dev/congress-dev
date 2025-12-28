'use client';

import { Card, Grid, Toolbar } from '@mui/material';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import { LegislationCalendar } from '~/app/_home/widgets/legislationCalendar';
import { LegislationTags } from '~/app/_home/widgets/legislationTags';

export function AuthedHomePage() {
	return (
		<>
			<Typography variant='h1'>Welcome back!</Typography>
			<Typography variant='subtitle2'>
				Your Gateway to Understanding Federal Legislation.
			</Typography>
			<Typography sx={{ mt: 2 }}>
				Welcome to Congress.dev, your trusted tool for exploring and
				understanding federal legislation. In a world where legislative
				processes can seem opaque and overwhelming, our platform
				provides clarity by offering an intuitive and powerful way to
				track, parse, and analyze federal bills and resolutions in real
				time. Whether you're a policy analyst, developer, journalist, or
				simply a curious citizen, we empower you with the tools to stay
				informed and engaged with the lawmaking process.
			</Typography>
			<Box
				sx={{
					display: { xs: 'block', md: 'flex' },
					mt: 2,
					gap: 2,
				}}
			>
				<Paper elevation={3} sx={{ flex: 1, p: 2 }}>
					<Box>
						<Typography variant='h2'>Dashboard</Typography>
						<Grid container spacing={2} sx={{ mt: 2 }}>
							<Grid size={4}>
								{' '}
								<Card>
									<Toolbar
										disableGutters
										sx={{
											height: '40px',
											minHeight: '40px',
											px: 2,
										}}
										variant='dense'
									>
										Top Legislation Tags
									</Toolbar>
									<Box sx={{ px: 3, pt: 1, pb: 2 }}>
										<LegislationTags />
									</Box>
								</Card>
							</Grid>
							<Grid size={8}>
								<Card>
									<Toolbar
										disableGutters
										sx={{
											height: '40px',
											minHeight: '40px',
											px: 2,
										}}
										variant='dense'
									>
										Legislation Calendar
									</Toolbar>
									<Box sx={{ px: 3, pt: 1, pb: 2 }}>
										<LegislationCalendar />
									</Box>
								</Card>
							</Grid>
							<Grid size={6}>
								<Card>
									<Toolbar
										disableGutters
										sx={{
											height: '40px',
											minHeight: '40px',
											px: 2,
										}}
										variant='dense'
									>
										Followed Legislation
									</Toolbar>
									<Box sx={{ px: 3, pt: 1, pb: 2 }}></Box>
								</Card>
							</Grid>
							<Grid size={6}>
								<Card>
									<Toolbar
										disableGutters
										sx={{
											height: '40px',
											minHeight: '40px',
											px: 2,
										}}
										variant='dense'
									>
										Followed Sponsors
									</Toolbar>
									<Box sx={{ px: 3, pt: 1, pb: 2 }}></Box>
								</Card>
							</Grid>
							<Grid size={12}>
								<Card>
									<Toolbar
										disableGutters
										sx={{
											height: '40px',
											minHeight: '40px',
											px: 2,
										}}
										variant='dense'
									>
										USC Tracking
									</Toolbar>
									<Box sx={{ px: 3, pt: 1, pb: 2 }}></Box>
								</Card>
							</Grid>
						</Grid>
					</Box>
				</Paper>
			</Box>
		</>
	);
}
