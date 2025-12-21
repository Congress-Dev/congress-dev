import AddchartIcon from '@mui/icons-material/Addchart';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { navigationLinks } from '~/constants';
import { HydrateClient } from '~/trpc/server';

export default async function Home() {
	return (
		<HydrateClient>
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
						<Typography variant='h1'>
							Welcome to Congress.dev
						</Typography>
						<Typography variant='subtitle2'>
							Your Gateway to Understanding Federal Legislation.
						</Typography>

						<Typography sx={{ mt: 2 }}>
							Welcome to Congress.dev, your trusted tool for
							exploring and understanding federal legislation. In
							a world where legislative processes can seem opaque
							and overwhelming, our platform provides clarity by
							offering an intuitive and powerful way to track,
							parse, and analyze federal bills and resolutions in
							real time. Whether you're a policy analyst,
							developer, journalist, or simply a curious citizen,
							we empower you with the tools to stay informed and
							engaged with the lawmaking process.
						</Typography>

						<Box
							sx={{
								display: { xs: 'block', md: 'flex' },
								mt: 2,
								gap: 2,
							}}
						>
							<Paper
								elevation={3}
								sx={{
									flexBasis: '20%',
									alignSelf: 'flex-start',
									mb: { xs: 1 },
								}}
							>
								<Box sx={{ p: 2 }}>
									<Typography variant='h2'>
										Key Features
									</Typography>
									<ul style={{ padding: '14px 20px' }}>
										<li>
											<b>Search Bills & Laws</b>
											<br />
											Easily find and explore federal
											legislation and its impact on the
											U.S. Code.
										</li>

										<li>
											<b>Track Your Interest</b>
											<br />
											Follow specific bills, lawmakers, or
											committees to stay informed.
										</li>

										<li>
											<b>Understand the Proces</b>
											<br />
											Learn how laws are made and track
											their progress through Congress.
										</li>
									</ul>
								</Box>
							</Paper>

							<Paper elevation={3} sx={{ flex: 1, p: 2 }}>
								<Box>
									<Typography variant='h2'>
										Getting Started
									</Typography>
									<p>
										At its core, the platform bridges the
										gap between raw legislative data and
										actionable insights. It collects and
										organizes information from official
										government sources, presenting it in an
										easily digestible and searchable format.
										From bill summaries to voting records,
										sponsor details, and legislative
										histories, we ensure you have the full
										context you need at your fingertips. For
										developers, the robust API enables
										seamless integration of legislative data
										into projects, fostering innovation and
										deeper analysis.
									</p>
									<p>
										Transparency and accessibility are at
										the heart of what we do. By demystifying
										federal legislation and making it
										available to everyone, we contribute to
										a more informed and engaged public. Join
										us in exploring the policies that shape
										our nation and discover how this
										resource can keep you connected to the
										legislative process.
									</p>
									<Box
										sx={{
											display: {
												xs: 'block',
												md: 'flex',
											},
											gap: 2,
										}}
									>
										<Paper
											sx={{
												flexBasis: '33%',
												p: 2,
												mb: { xs: 1 },
											}}
										>
											<Box
												sx={{
													display: 'flex',
													alignItems: 'center',
													gap: 1,
												}}
											>
												<AutoAwesomeIcon />
												<Typography variant='h5'>
													Explore Legislation
												</Typography>
											</Box>
											<p>
												Dive into the details of federal
												bills and resolutions shaping
												the nation's future.
											</p>
											<Link href='/congress/bills'>
												<Button
													size='small'
													variant='contained'
												>
													Search Bills
												</Button>
											</Link>
										</Paper>

										<Paper
											sx={{
												flexBasis: '33%',
												p: 2,
												mb: { xs: 1 },
											}}
										>
											<Box
												sx={{
													display: 'flex',
													alignItems: 'center',
													gap: 1,
												}}
											>
												<AddchartIcon />
												<Typography variant='h5'>
													Customize Your Experience
												</Typography>
											</Box>

											<p>
												Track the legislation and
												lawmakers that matter to you.
											</p>
											<Link href='#'>
												<Button
													color='primary'
													size='small'
													variant='contained'
												>
													Login
												</Button>
											</Link>
										</Paper>
									</Box>
								</Box>
							</Paper>
						</Box>
					</Paper>
				</Container>
			</Box>
		</HydrateClient>
	);
}
