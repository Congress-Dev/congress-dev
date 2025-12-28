import { Box, List, ListItem, ListItemButton, Typography } from '@mui/material';
import Link from 'next/link';
import { api } from '~/trpc/react';
import { DashboardWidgetContent } from './';

export function LegislationFollowed() {
	const { data, isLoading, isError } = api.user.legislationFeed.useQuery();

	return (
		<DashboardWidgetContent
			isEmpty={data?.length === 0}
			isError={isError}
			isLoading={isLoading}
		>
			{data && (
				<List dense>
					{data.map((bill) => {
						const legislator =
							bill?.legislation_sponsorship[0]?.legislator;

						return (
							<ListItem disablePadding key={bill?.legislation_id}>
								<ListItemButton>
									<Link
										href={`/congress/bills/${bill?.legislation_id}`}
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
												{bill?.title}
											</Typography>
											<Typography variant='caption'>
												{`${bill?.congress?.session_number}th - `}
												{bill?.chamber === 'House'
													? 'H.R'
													: 'S'}
												{'. #'}
												{bill?.number}
												{' by '}
												{`${legislator?.first_name} ${legislator?.last_name}`}
											</Typography>
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
