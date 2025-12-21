import CommitIcon from '@mui/icons-material/Commit';
import MergeTypeIcon from '@mui/icons-material/MergeType';

import { Box, Chip, Container, Paper, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { BillTabs } from '~/app/congress/bills/[billId]/tabs';
import { BillVersionEnum } from '~/enums';
import { api, HydrateClient } from '~/trpc/server';

export default async function BillLayout({
	params,
	children,
}: {
	params: Promise<Params>;
	children: React.ReactNode;
}) {
	const { billId } = await params;

	const data = await api.bill.get({
		id: Number(billId as string),
	});

	console.log(data.legislation_action);

	const latestVersion =
		data.legislation_version[data.legislation_version.length - 1];
	const legislator = data.legislation_sponsorship.find(
		(sponsor) => !sponsor.cosponsor,
	)?.legislator;

	return (
		<HydrateClient>
			<Container maxWidth='xl'>
				<Box sx={{ display: 'flex', alignItems: 'center' }}>
					<Typography sx={{ mr: 1 }} variant='h1'>
						{data?.title}
					</Typography>
					<Typography
						sx={{ fontWeight: 100, color: '#8f99a8' }}
						variant='h1'
					>
						{`#${data?.number}`}
					</Typography>
				</Box>
				<Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
					{data.signed ? (
						<>
							<Chip
								color='info'
								label={
									<Box
										sx={{
											display: 'flex',
											alignItems: 'center',
										}}
									>
										<MergeTypeIcon
											fontSize='small'
											sx={{ ml: -1, mr: 0.5 }}
										/>
										{'Signed'}
									</Box>
								}
								size='small'
								sx={{ px: 1, mr: 1 }}
							/>
							<Typography variant='caption'>
								{data.signed.text}
							</Typography>
						</>
					) : (
						<>
							<Chip
								color='warning'
								label={
									<Box
										sx={{
											display: 'flex',
											alignItems: 'center',
										}}
									>
										<CommitIcon
											fontSize='small'
											sx={{ ml: -1, mr: 0.5 }}
										/>
										{latestVersion?.legislation_version
											? BillVersionEnum[
													latestVersion
														?.legislation_version
												]
											: 'Unknown'}
									</Box>
								}
								size='small'
								sx={{ px: 1, mr: 1 }}
							/>
							<Typography variant='caption'>
								Proposed by{' '}
								{legislator?.job === 'Senator'
									? 'Sen.'
									: 'Rep.'}{' '}
								{`${legislator?.first_name} ${legislator?.last_name}`}{' '}
								in the {data.chamber}
								{latestVersion?.effective_date
									? `, effective ${latestVersion?.effective_date.toLocaleDateString()}`
									: ''}
							</Typography>
						</>
					)}
				</Box>

				<BillTabs />
				<Paper
					elevation={0}
					sx={{
						p: 2,
						mb: 3,
						borderTop: 'none',
						borderTopLeftRadius: '0px',
					}}
				>
					{children}
				</Paper>
			</Container>
		</HydrateClient>
	);
}
