'use client';
import { Button } from '@mui/material';
import { api } from '~/trpc/react';

export function LegislationFollow({
	legislation_id,
}: {
	legislation_id: number;
}) {
	const utils = api.useUtils();

	const { data: following, isFetching } =
		api.user.legislationFollowing.useQuery({
			legislation_id,
		});

	const mutation = api.user.legislationFollow.useMutation({
		onSuccess: () => {
			utils.user.legislationFollowing.invalidate();
		},
	});

	return (
		<Button
			disabled={isFetching || mutation.isPending}
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
			{following ? 'Unfollow' : 'Follow'}
		</Button>
	);
}
