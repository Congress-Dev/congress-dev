'use client';

import {
	Box,
	Button,
	List,
	ListItem,
	ListItemButton,
	Typography,
} from '@mui/material';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import type { RouterOutputs } from '~/trpc/react';
import { api } from '~/trpc/react';
import { DashboardWidgetContent } from './';

type InterestBill = RouterOutputs['user']['interestLegislation'][number];

function matchedSummary(bill: InterestBill): string {
	const headings = Object.values(bill.matched_headings ?? {});
	if (headings.length > 0) {
		const display = headings.slice(0, 2).join(', ');
		const extra = headings.length > 2 ? ` +${headings.length - 2}` : '';
		return `${display}${extra}`;
	}
	const idents = bill.matched_idents ?? [];
	if (idents.length > 0) {
		const slugs = idents
			.slice(0, 2)
			.map((id: string) => id.split('/').slice(3).join('/'));
		const extra = idents.length > 2 ? ` +${idents.length - 2}` : '';
		return `${slugs.join(', ')}${extra}`;
	}
	return '';
}

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
					No bills found yet. Set up your interests to track relevant
					legislation.
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
					{data.slice(0, 8).map((bill: InterestBill) => {
						const summary = matchedSummary(bill);
						return (
							<ListItem disablePadding key={bill.legislation_id}>
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
											<Box
												sx={{
													display: 'flex',
													alignItems: 'center',
													gap: 1,
												}}
											>
												<Typography variant='caption'>
													{`${bill.session_number}th · `}
													{bill.chamber === 'house'
														? 'H.R.'
														: 'S.'}
													{` #${bill.number}`}
												</Typography>
												{summary && (
													<Typography
														color='textSecondary'
														sx={{
															overflow: 'hidden',
															textOverflow:
																'ellipsis',
															whiteSpace:
																'nowrap',
														}}
														variant='caption'
													>
														· {summary}
													</Typography>
												)}
											</Box>
										</Box>
									</Link>
								</ListItemButton>
							</ListItem>
						);
					})}
				</List>
			)}
		</DashboardWidgetContent>
	);
}
