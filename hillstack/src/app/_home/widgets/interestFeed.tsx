'use client';

import { Box, Button, List, ListItem, ListItemButton, Typography } from '@mui/material';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import type { RouterOutputs } from '~/trpc/react';
import { api } from '~/trpc/react';
import { DashboardWidgetContent } from './';

type InterestBill = RouterOutputs['user']['interestLegislation'][number];

export function InterestFeed() {
	const { data: session } = useSession();
	const { data, isLoading, isError } = api.user.interestLegislation.useQuery(
		undefined,
		{ enabled: Boolean(session) },
	);

	if (!session) {
		return (
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					justifyContent: 'center',
					height: 220,
					gap: 1,
				}}
			>
				<Typography color='textDisabled' variant='body2'>
					Log in to track legislation by interest
				</Typography>
			</Box>
		);
	}

	if (!isLoading && !isError && data?.length === 0) {
		return (
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignItems: 'center',
					justifyContent: 'center',
					height: 220,
					gap: 1,
					px: 2,
				}}
			>
				<Typography
					color='textDisabled'
					textAlign='center'
					variant='body2'
				>
					No bills found yet. Set up your interests to track
					relevant legislation.
				</Typography>
				<Button
					component={Link}
					href='/user/interests'
					size='small'
					variant='outlined'
				>
					Set up interests
				</Button>
			</Box>
		);
	}

	return (
		<DashboardWidgetContent
			isEmpty={(data?.length ?? 0) === 0}
			isError={isError}
			isLoading={isLoading}
		>
			{data && (
				<List dense>
					{data.slice(0, 8).map((bill: InterestBill) => (
						<ListItem
							disablePadding
							key={bill.legislation_id}
						>
							<ListItemButton>
								<Link
									href={`/congress/bills/${bill.legislation_id}`}
									style={{
										width: '100%',
										display: 'block',
									}}
								>
									<Box
										sx={{
											display: 'flex',
											flexDirection: 'column',
										}}
									>
										<Typography color='primary'>
											{bill.title}
										</Typography>
										<Typography variant='caption'>
											{`${bill.session_number}th · `}
											{bill.chamber === 'house'
												? 'H.R.'
												: 'S.'}
											{` #${bill.number}`}
										</Typography>
									</Box>
								</Link>
							</ListItemButton>
						</ListItem>
					))}
				</List>
			)}
		</DashboardWidgetContent>
	);
}
