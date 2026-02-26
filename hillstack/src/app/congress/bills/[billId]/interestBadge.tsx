'use client';

import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import { Chip, Tooltip } from '@mui/material';
import { useSession } from 'next-auth/react';
import { api } from '~/trpc/react';

export function InterestBadge({ legislationId }: { legislationId: number }) {
	const { data: session } = useSession();

	const { data } = api.user.interestBillMatch.useQuery(
		{ legislation_id: legislationId },
		{ enabled: Boolean(session) },
	);

	if (!session || !data?.matches) return null;

	return (
		<Tooltip
			title={`Touches your interest areas: ${data.matchedIdents.join(', ')}`}
		>
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
