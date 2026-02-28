import type { SvgIconComponent } from '@mui/icons-material';
import Diversity2Icon from '@mui/icons-material/Diversity2';
import EventSeatIcon from '@mui/icons-material/EventSeat';
import HowToVoteIcon from '@mui/icons-material/HowToVote';
import InfoOutlineIcon from '@mui/icons-material/InfoOutline';
import ReadMoreIcon from '@mui/icons-material/ReadMore';
import SummarizeIcon from '@mui/icons-material/Summarize';
import { Box, Chip, Divider, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import Link from 'next/link';
import { LegislationFollow } from '~/app/congress/bills/[billId]/overview/follow';
import { Timeline, TimelineNode } from '~/components/timeline';
import { BillVersionEnum } from '~/enums';
import { api, HydrateClient } from '~/trpc/server';

export default async function BillOverviewPage({
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

	const summary =
		latestVersion?.legislation_content[0]?.legislation_content_summary[0]
			?.summary;

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
							summary ?? 'No summary was found for this bill'
						}
						icon={<SummarizeIcon />}
						title='Summary'
					>
						{data?.legislation_version?.map((version) => (
							<TimelineNode
								date={
									version.effective_date ??
									version.created_at ??
									new Date()
								}
								icon={ReadMoreIcon}
								key={version.legislation_version}
								title={
									version.legislation_version
										? `Legislation has been ${BillVersionEnum[version.legislation_version]}`
										: 'Unknown legislation version'
								}
								variant='compact'
							/>
						))}
						{data?.legislation_vote?.map((vote) => {
							const voteTotal = JSON.parse(vote.total as string);

							return (
								<TimelineNode
									date={vote.datetime ?? new Date()}
									icon={HowToVoteIcon}
									key={vote.id}
									title={`${vote.chamber} voted on ${vote.question}`}
								>
									{`The vote ${vote.passed ? 'passed' : 'failed'} ${voteTotal.yay}-${voteTotal.nay}, with ${voteTotal.abstain} not voting.`}
								</TimelineNode>
							);
						})}
						{data?.legislation_action?.map((action) => {
							const iconMap: Record<string, SvgIconComponent> = {
								President: EventSeatIcon,
								Committee: Diversity2Icon,
								IntroReferral: Diversity2Icon,
							};

							let icon: SvgIconComponent = InfoOutlineIcon;

							if (
								action.action_type &&
								iconMap[action.action_type]
							) {
								const iconCandidate =
									iconMap[action.action_type];
								if (iconCandidate) {
									icon = iconCandidate;
								}
							}

							return (
								<TimelineNode
									date={action.action_date ?? new Date()}
									icon={icon}
									key={action.legislation_action_id}
									title={
										action.text ??
										'Unknown legislation action'
									}
									variant='compact'
								/>
							);
						})}
					</Timeline>
				</Box>
				<Box
					sx={{
						width: '300px',
						pl: 3,
						pr: 2,
						display: { xs: 'none', md: 'block' },
					}}
				>
					<LegislationFollow
						legislation_id={Number(billId as string)}
					/>
					<Box
						sx={{
							mb: 1,
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Typography variant='subtitle2'>Sponsor:</Typography>
						<Typography color='primary' variant='subtitle1'>
							<Link
								href={`/congress/legislators/${sponsor?.legislator?.bioguide_id}`}
							>
								{sponsor?.legislator?.first_name}{' '}
								{sponsor?.legislator?.last_name}
							</Link>
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
							<Box
								sx={{
									display: 'flex',
									gap: 0.5,
									mt: 0.5,
									flexWrap: 'wrap',
								}}
							>
								{latestVersion?.legislation_version_tag[0]?.tags.map(
									(tag) => (
										<Chip
											color='primary'
											key={tag}
											label={tag}
											size='small'
											variant='outlined'
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
							<Box
								sx={{
									display: 'flex',
									gap: 0.5,
									mt: 0.5,
									flexWrap: 'wrap',
								}}
							>
								{data.legislative_policy_area_association.map(
									(assc) => (
										<Chip
											color='primary'
											key={
												assc.legislative_policy_area
													?.name
											}
											label={
												assc.legislative_policy_area
													?.name
											}
											size='small'
											variant='outlined'
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
