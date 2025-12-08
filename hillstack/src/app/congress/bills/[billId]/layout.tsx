import { Box, Chip, Container, Paper, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
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

	const latestVersion =
		data.legislation_version[data.legislation_version.length - 1];
	const legislator = data.legislation_sponsorship.find(
		(sponsor) => !sponsor.cosponsor,
	)?.legislator;

	return (
		<HydrateClient>
			<Container maxWidth='xl'>
				<Box sx={{ display: 'flex', alignItems: 'center' }}>
					<Typography color='primary' sx={{ mr: 1 }} variant='h1'>
						{data?.title}
					</Typography>
					<Typography sx={{ fontWeight: 300 }} variant='h1'>
						{`#${data?.number}`}
					</Typography>
				</Box>
				<Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
					<Chip
						label={
							latestVersion?.legislation_version
								? BillVersionEnum[
										latestVersion?.legislation_version
									]
								: 'Unknown'
						}
						size='small'
						sx={{ px: 1, mr: 1 }}
					/>
					<Typography variant='caption'>
						Proposed by{' '}
						{legislator?.job === 'Senator' ? 'Sen.' : 'Rep.'}{' '}
						{`${legislator?.first_name} ${legislator?.last_name}`}{' '}
						in the {data.chamber}
						{latestVersion?.effective_date
							? `, effective ${latestVersion?.effective_date.toLocaleDateString()}`
							: ''}
					</Typography>
				</Box>
				<Paper elevation={0} sx={{ mt: 2, p: 2 }}>
					{children}
				</Paper>
			</Container>
		</HydrateClient>
	);
}
