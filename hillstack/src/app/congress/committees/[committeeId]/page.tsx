import PhoneIcon from '@mui/icons-material/Phone';
import PlaceIcon from '@mui/icons-material/Place';
import PublicIcon from '@mui/icons-material/Public';
import YouTubeIcon from '@mui/icons-material/YouTube';
import {
	Box,
	Button,
	Card,
	Container,
	Divider,
	List,
	ListItem,
	ListItemButton,
	Toolbar,
	Typography,
} from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import Link from 'next/link';
import { api, HydrateClient } from '~/trpc/server';

export default async function CommitteePage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { committeeId } = await params;
	const data = await api.committee.get({
		id: Number(committeeId),
	});

	return (
		<HydrateClient>
			<Container maxWidth='xl'>
				<Box sx={{ display: { xs: 'block', md: 'flex' }, gap: 3 }}>
					<Box
						sx={{
							flexBasis: '300px',
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Box
							sx={{
								display: 'flex',
								justifyContent: { xs: 'center', md: 'left' },
							}}
						>
							{/* <Avatar
								src={data.image_url ?? ''}
								sx={{ width: '200px', height: '200px' }}
							/> */}
						</Box>
						<Box sx={{ mt: 3 }}>
							<Typography variant='h1'>{`${data.name}`}</Typography>
							{data.chamber && (
								<Typography
									color='textDisabled'
									sx={{ fontWeight: 100 }}
									variant='h2'
								>
									U.S. {data.chamber}
								</Typography>
							)}
						</Box>
						<Box sx={{ mt: 2, mb: 3 }}>
							{data.url && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
										mb: 1,
									}}
								>
									<PublicIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography
										color='primary'
										sx={{ lineHeight: 1 }}
										variant='subtitle1'
									>
										<a href={data.url} target='_blank'>
											{data.url}
										</a>
									</Typography>
								</Box>
							)}
							{data.address && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
										mb: 1,
									}}
								>
									<PlaceIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography
										sx={{ lineHeight: 1 }}
										variant='subtitle1'
									>
										{data.address}
									</Typography>
								</Box>
							)}
							{data.phone && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<PhoneIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography
										sx={{ lineHeight: 1 }}
										variant='subtitle1'
									>
										<a
											href={`tel:${data.phone}`}
											target='_blank'
										>
											{data.phone}
										</a>
									</Typography>
								</Box>
							)}
						</Box>
						<Button size='small' variant='outlined'>
							Follow
						</Button>
						{data.jurisdiction && (
							<>
								<Box
									sx={{
										my: 3,
									}}
								>
									<Typography variant='subtitle1'>
										{data.jurisdiction}
									</Typography>
								</Box>
								<Divider />
							</>
						)}
						<Box
							sx={{
								mt: 3,
								display: 'flex',
								flexDirection: 'column',
								gap: 1,
							}}
						>
							{data?.youtube_id && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<YouTubeIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography variant='subtitle1'>
										<a
											href={`https://youtube.com/channels/${data.youtube_id}`}
											target='_blank'
										>
											YouTube Channel
										</a>
									</Typography>
								</Box>
							)}
						</Box>
					</Box>
					<Box sx={{ flexGrow: 1, my: { xs: 3 } }}>
						{data.subcommittees.length > 0 && (
							<Card sx={{ mb: 2 }} variant='outlined'>
								<Toolbar
									disableGutters
									sx={{
										px: 2,
										height: '35px',
										minHeight: '35px',
										display: 'flex',
									}}
									variant='dense'
								>
									Subcommittees
								</Toolbar>
								<List dense>
									{data.subcommittees.map((subcommittee) => (
										<ListItem
											disablePadding
											key={
												subcommittee.legislation_committee_id
											}
										>
											<ListItemButton>
												<Link
													href={`/congress/committees/${subcommittee.legislation_committee_id}`}
													style={{
														width: '100%',
														display: 'block',
													}}
												>
													<Box
														sx={{
															display: 'flex',
															flexDirection:
																'column',
														}}
													>
														<Typography color='primary'>
															{subcommittee.name}
														</Typography>
														<Typography variant='caption'>
															{subcommittee.chamber
																? `U.S. ${subcommittee.chamber}`
																: 'Unknown Chamber'}
														</Typography>
													</Box>
												</Link>
											</ListItemButton>
										</ListItem>
									))}
								</List>
							</Card>
						)}
						{data.legislation.length > 0 && (
							<Card variant='outlined'>
								<Toolbar
									disableGutters
									sx={{
										px: 2,
										height: '35px',
										minHeight: '35px',
										display: 'flex',
									}}
									variant='dense'
								>
									Recent Legislation
								</Toolbar>
								<List dense>
									{data.legislation.map((bill) => (
										<ListItem
											disablePadding
											key={bill?.legislation_id}
										>
											<ListItemButton>
												<Link
													href={`/congress/bills/${bill?.legislation_id}`}
													style={{
														width: '100%',
														display: 'block',
													}}
												>
													<Box
														sx={{
															display: 'flex',
															flexDirection:
																'column',
														}}
													>
														<Typography color='primary'>
															{bill?.title}
														</Typography>
														<Typography variant='caption'>
															{`${bill?.congress?.session_number}th - `}
															{bill?.chamber ===
															'House'
																? 'H.R'
																: 'S'}
															{'. #'}
															{bill?.number}
														</Typography>
													</Box>
												</Link>
											</ListItemButton>
										</ListItem>
									))}
								</List>
							</Card>
						)}
					</Box>
				</Box>
			</Container>
		</HydrateClient>
	);
}
