import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import type { inferRouterOutputs } from '@trpc/server';
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
									<Typography color='primary' variant='h2'>
										{committee.name}
									</Typography>
									<Box>
										<Typography variant='subtitle2'>
											Congress:
										</Typography>{' '}
										{/* <Typography variant='subtitle1'>
											{committee.congressId}
										</Typography> */}
									</Box>
									<Box>
										<Typography variant='subtitle2'>
											Thomas Id:
										</Typography>{' '}
										{/* <Typography variant='subtitle1'>
											{committee.thomasId}
										</Typography> */}
									</Box>
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
