import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import type { inferRouterOutputs } from '@trpc/server';
import Link from 'next/link';
import type { AppRouter } from '~/server/api/root';

export interface CommitteeSearchResultProps {
	committee: inferRouterOutputs<AppRouter>['committee']['search']['committees'][0];
}

export function CommitteeSearchResult({
	committee,
}: CommitteeSearchResultProps) {
	return (
		<>
			<ListItem component='div' disablePadding>
				<ListItemButton>
					<ListItemText
						primary={
							<Box sx={{ display: 'flex' }}>
								<Box flexGrow={1} sx={{ pl: 2 }}>
									<Link
										href={`/congress/committees/${committee.legislation_committee_id}`}
									>
										<Typography
											color='primary'
											variant='h4'
										>
											{committee.name}
										</Typography>
										<Typography variant='caption'>
											{committee.chamber
												? `U.S. ${committee.chamber}`
												: 'Unknown Chamber'}
										</Typography>
									</Link>
								</Box>
							</Box>
						}
					/>
				</ListItemButton>
			</ListItem>
			<Divider />
		</>
	);
}
