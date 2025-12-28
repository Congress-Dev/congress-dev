'use client';
import { Button } from '@mui/material';
import { api } from '~/trpc/react';

export function LegislatorFollow({ bioguide_id }: { bioguide_id: string }) {
	const utils = api.useUtils();

	const { data: following, isFetching } =
		api.user.legislatorFollowing.useQuery({
			bioguide_id,
		});

	const mutation = api.user.legislatorFollow.useMutation({
		onSuccess: () => {
			utils.user.legislatorFollowing.invalidate();
		},
	});

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
