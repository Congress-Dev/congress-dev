'use client';

import { Button, Divider } from '@mui/material';
import { useSession } from 'next-auth/react';
import { api } from '~/trpc/react';

export function LegislationFollow({
	legislation_id,
}: {
	legislation_id: number;
}) {
	const utils = api.useUtils();
	const { data: session } = useSession();

	const { data: following, isFetching } =
		api.user.legislationFollowing.useQuery(
			{
				legislation_id,
			},
			{
				enabled: Boolean(session),
			},
		);

	const mutation = api.user.legislationFollow.useMutation({
		onSuccess: () => {
			utils.user.legislationFollowing.invalidate();
			utils.user.legislationFeed.invalidate();
		},
	});

	return (
		<>
			<Button
				disabled={!session || isFetching || mutation.isPending}
				loading={isFetching || mutation.isPending}
				onClick={() => {
					mutation.mutate({
						legislation_id,
					});
				}}
				size='small'
				sx={{ width: '100%', mb: 2 }}
				variant={following ? 'contained' : 'outlined'}
			>
				{!session ? 'Login to Follow' : following ? 'Unfollow' : 'Follow'}
			</Button>
			<Divider sx={{ mb: 1 }} />
		</>
	);
}
