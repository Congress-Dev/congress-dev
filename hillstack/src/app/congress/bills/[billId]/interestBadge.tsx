'use client';

import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import { Box, Chip, Tooltip, Typography } from '@mui/material';
import { useSession } from 'next-auth/react';
import { api } from '~/trpc/react';

function truncateInterest(text: string, maxLen = 60): string {
	if (text.length <= maxLen) return text;
	return `${text.slice(0, maxLen).trimEnd()}…`;
}

export function InterestBadge({ legislationId }: { legislationId: number }) {
	const { data: session } = useSession();

	const { data } = api.user.interestBillMatch.useQuery(
		{ legislation_id: legislationId },
		{ enabled: Boolean(session) },
	);

	if (!session || !data?.matches) return null;

	const hasHeadings = Object.keys(data.matchedHeadings).length > 0;
	const interestLabel = data.interestText
		? truncateInterest(data.interestText)
		: '';

	const tooltipContent = (
		<Box sx={{ maxWidth: 360 }}>
			{interestLabel && (
				<Typography sx={{ mb: 0.5 }} variant='caption'>
					Related to your interest in "{interestLabel}"
				</Typography>
			)}
			{hasHeadings ? (
				<Box component='ul' sx={{ m: 0, pl: 2 }}>
					{data.matchedIdents.slice(0, 5).map((ident: string) => {
						const heading = data.matchedHeadings[ident];
						const slug = ident.split('/').slice(3).join('/');
						return (
							<li key={ident}>
								<Typography variant='caption'>
									{heading ? `${slug} — ${heading}` : slug}
								</Typography>
							</li>
						);
					})}
					{data.matchedIdents.length > 5 && (
						<li>
							<Typography color='textSecondary' variant='caption'>
								+{data.matchedIdents.length - 5} more
							</Typography>
						</li>
					)}
				</Box>
			) : (
				<Typography variant='caption'>
					Touches: {data.matchedIdents.slice(0, 3).join(', ')}
					{data.matchedIdents.length > 3 &&
						` +${data.matchedIdents.length - 3} more`}
				</Typography>
			)}
		</Box>
	);

	return (
		<Tooltip title={tooltipContent}>
			<Chip
				color='success'
				icon={<TrackChangesIcon />}
				label='Matches your interests'
				size='small'
				sx={{ px: 1, mr: 1, mt: { xs: 0.5, md: 0 } }}
			/>
		</Tooltip>
	);
}
