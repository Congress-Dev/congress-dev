import HowToVoteIcon from '@mui/icons-material/HowToVote';
import ReadMoreIcon from '@mui/icons-material/ReadMore';
import SummarizeIcon from '@mui/icons-material/Summarize';
import { Box, Chip, Divider, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { Timeline, TimelineNode } from '~/components/timeline';
import { BillVersionEnum } from '~/enums';
import { api, HydrateClient } from '~/trpc/server';

export default async function BillPageOverview({
	params,
}: {
	params: Promise<Params>;
}) {
	const { billId } = await params;
	const data = await api.bill.get({
		id: Number(billId as string),
	});

	const latestVersion =
		data.legislation_version[data.legislation_version.length - 1];

	const sponsor = data.legislation_sponsorship.find(
		(sponsor) => !sponsor.cosponsor,
	);
	const cosponsors = data.legislation_sponsorship
		.filter((sponsor) => sponsor.cosponsor)
		?.slice(0, 5);

	return (
		<HydrateClient>
			<Box sx={{ display: 'flex' }}>
				<Box sx={{ flex: 1 }}>
					<Timeline
						content={
							data?.legislation_version[0]?.legislation_content[0]
								?.legislation_content_summary[0]?.summary ??
							'No summary was found for this bill'
						}
						icon={<SummarizeIcon />}
						title='Summary'
					>
						{data?.legislation_version?.map((version) => (
							<TimelineNode
								date={
									version.created_at ??
									new Date(version.effective_date) ??
									new Date()
								}
								icon={<ReadMoreIcon />}
								key={version.legislation_version}
								title={
									version.legislation_version
										? `Legislation has been ${BillVersionEnum[version.legislation_version]}`
										: 'Unknown legislation action'
								}
								variant='compact'
							/>
						))}
						{data?.legislation_vote?.map((vote) => {
							const voteTotal = JSON.parse(vote.total as string);

							return (
								<TimelineNode
									date={vote.datetime}
									icon={<HowToVoteIcon />}
									key={vote.id}
									title={`${vote.chamber} voted on ${vote.question}`}
								>
									{`The vote ${vote.passed ? 'passed' : 'failed'} ${voteTotal.yay}-${voteTotal.nay}, with ${voteTotal.abstain} not voting.`}
								</TimelineNode>
							);
						})}
					</Timeline>
				</Box>
				<Box sx={{ width: '300px', pl: 3, pr: 2 }}>
					<Box
						sx={{
							mb: 1,
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Typography variant='subtitle2'>Sponsor:</Typography>
						<Typography variant='subtitle1'>
							{sponsor?.legislator?.first_name}{' '}
							{sponsor?.legislator?.last_name}
						</Typography>
					</Box>
					<Divider />
					<Box
						sx={{
							my: 1,
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Typography variant='subtitle2'>
							Co-Sponsors:
						</Typography>
						<Typography variant='subtitle1'>
							{cosponsors.length
								? cosponsors?.map((sponsor) => (
										<Box
											key={
												sponsor.legislator?.bioguide_id
											}
										>
											{sponsor.legislator?.first_name}{' '}
											{sponsor.legislator?.last_name}
										</Box>
									))
								: 'None'}
						</Typography>
					</Box>
					<Divider />
					<Box
						sx={{
							my: 1,
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Typography variant='subtitle2'>Tags:</Typography>

						{latestVersion?.legislation_version_tag.length ? (
							<Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
								{latestVersion?.legislation_version_tag[0]?.tags.map(
									(tag) => (
										<Chip
											key={tag}
											label={tag}
											size='small'
										/>
									),
								)}
							</Box>
						) : (
							'None'
						)}
					</Box>
					<Divider />
					<Box
						sx={{ my: 1, display: 'flex', flexDirection: 'column' }}
					>
						<Typography variant='subtitle2'>
							Policy Areas:
						</Typography>

						{data.legislative_policy_area_association.length ? (
							<Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
								{data.legislative_policy_area_association.map(
									(assc) => (
										<Chip
											key={
												assc.legislative_policy_area
													?.name
											}
											label={
												assc.legislative_policy_area
													?.name
											}
											size='small'
										/>
									),
								)}
							</Box>
						) : (
							'None'
						)}
					</Box>
				</Box>
			</Box>
		</HydrateClient>
	);
}
