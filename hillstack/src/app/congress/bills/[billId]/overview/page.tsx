import HowToVoteIcon from '@mui/icons-material/HowToVote';
import SummarizeIcon from '@mui/icons-material/Summarize';
import { Avatar, Box, Card, Divider, Toolbar, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { api } from '~/trpc/server';

export default async function BillPageOverview({
	params,
}: {
	params: Promise<Params>;
}) {
	const { billId } = await params;
	const data = await api.bill.get({
		id: Number(billId as string),
	});

	const sponsor = data.legislation_sponsorship.find(
		(sponsor) => !sponsor.cosponsor,
	);
	const cosponsors = data.legislation_sponsorship
		.filter((sponsor) => sponsor.cosponsor)
		?.slice(0, 5);

	return (
		<Box sx={{ display: 'flex' }}>
			<Box sx={{ flex: 1 }}>
				<Box sx={{ display: 'flex' }}>
					<Avatar sx={{ width: '40px', height: '40px', mr: 1 }}>
						<SummarizeIcon />
					</Avatar>
					<Card sx={{ flex: 1 }} variant='outlined'>
						<Toolbar
							disableGutters
							sx={{ height: '40px', minHeight: '40px', px: 2 }}
							variant='dense'
						>
							{'Summary'}
						</Toolbar>
						<Box sx={{ p: 2 }}>
							{data?.legislation_version[0]?.legislation_content.flatMap(
								(s) =>
									s.legislation_content_summary.flatMap(
										(b) => b.summary,
									)[0],
							)}
						</Box>
					</Card>
				</Box>
				<Box sx={{ pl: 5, mt: 2 }}>
					{data?.legislation_vote?.map((vote, index) => {
						const voteTotal = JSON.parse(vote.total as string);

						return (
							<Box key={vote.id} sx={{ display: 'flex', mb: 1 }}>
								<Box
									sx={{
										display: 'flex',
										flexDirection: 'column',
										alignContent: 'center',
										mr: 1,
									}}
								>
									<Avatar
										sx={{
											width: '30px',
											height: '30px',
										}}
									>
										<HowToVoteIcon />
									</Avatar>
									<Divider
										orientation='vertical'
										sx={{
											mt: 1,
											flex: 1,
											width: 'calc(50% + 1px)',
											borderRightWidth: '2px',
											display:
												index ===
												data.legislation_vote.length - 1
													? 'none'
													: 'initial',
										}}
									/>
								</Box>
								<Card
									sx={{ flex: 1, mb: 2 }}
									variant='outlined'
								>
									<Toolbar
										disableGutters
										sx={{
											height: '30px',
											minHeight: '30px',
											px: 1,
										}}
										variant='dense'
									>
										{`${vote.chamber} voted on ${vote.question}`}
									</Toolbar>
									<Box sx={{ p: 1 }}>
										The vote{' '}
										{vote.passed ? 'passed' : 'failed'}{' '}
										{voteTotal.yay}
										{`-`}
										{voteTotal.nay}
										{`, with `}
										{voteTotal.abstain}
										{` members not voting. `}
									</Box>
								</Card>
							</Box>
						);
					})}
				</Box>
			</Box>
			<Box sx={{ width: '300px', pl: 3, pr: 2 }}>
				<Box sx={{ mb: 1 }}>
					<Typography variant='subtitle2'>Sponsor:</Typography>
					<Typography variant='subtitle1'>
						{sponsor?.legislator?.first_name}{' '}
						{sponsor?.legislator?.last_name}
					</Typography>
				</Box>
				<Divider />
				<Box sx={{ my: 1 }}>
					<Typography variant='subtitle2'>Co-Sponsors:</Typography>
					<Typography variant='subtitle1'>
						{cosponsors?.map((sponsor) => (
							<Box key={sponsor.legislator?.bioguide_id}>
								{sponsor.legislator?.first_name}{' '}
								{sponsor.legislator?.last_name}
							</Box>
						))}
					</Typography>
				</Box>
				<Divider />
				<Box sx={{ my: 1 }}>
					<Typography variant='subtitle2'>Tags:</Typography>
				</Box>
				<Divider />
				<Box sx={{ my: 1 }}>
					<Typography variant='subtitle2'>Policy Areas:</Typography>
				</Box>
			</Box>
		</Box>
	);
}
