'use client';
import { Button } from '@mui/material';
import { useSession } from 'next-auth/react';
import { api } from '~/trpc/react';

export function LegislatorFollow({ bioguide_id }: { bioguide_id: string }) {
	const utils = api.useUtils();
	const { data: session } = useSession();

	const { data: following, isFetching } =
		api.user.legislatorFollowing.useQuery(
			{
				bioguide_id,
			},
			{
				enabled: Boolean(session),
			},
		);

	const mutation = api.user.legislatorFollow.useMutation({
		onSuccess: () => {
			utils.user.legislatorFollowing.invalidate();
		},
	});

	if (!session) {
		return;
	}

	return (
		<Button
			disabled={isFetching || mutation.isPending}
			loading={isFetching || mutation.isPending}
			onClick={() => {
				mutation.mutate({
					bioguide_id,
				});
			}}
			size='small'
			variant={following ? 'contained' : 'outlined'}
		>
			{following ? 'Unfollow' : 'Follow'}
		</Button>
	);
}
