import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import type { inferRouterOutputs } from '@trpc/server';
import type { AppRouter } from '~/server/api/root';

export interface LegislatorSearchResultProps {
	legislator: inferRouterOutputs<AppRouter>['legislator']['search']['members'][0];
}

export function LegislatorSearchResult({
	legislator,
}: LegislatorSearchResultProps) {
	return (
		<>
			<ListItem component='div' disablePadding>
				<ListItemButton>
					<ListItemText
						primary={
							<Box sx={{ display: 'flex' }}>
								<Avatar
									src={legislator.image_url ?? ''}
									sx={{ width: '75px', height: '75px' }}
								/>
								<Box flexGrow={1} sx={{ pl: 2 }}>
									<Typography color='primary' variant='h2'>
										{legislator.last_name},{' '}
										{legislator.first_name}
									</Typography>
									<Box>
										<Typography variant='subtitle2'>
											Job:
										</Typography>{' '}
										<Typography variant='subtitle1'>
											{legislator.job}
										</Typography>
									</Box>
									<Box>
										<Typography variant='subtitle2'>
											Party:
										</Typography>{' '}
										<Typography variant='subtitle1'>
											{legislator.party}
										</Typography>
									</Box>
									<Box>
										<Typography variant='subtitle2'>
											State:
										</Typography>{' '}
										<Typography variant='subtitle1'>
											{legislator.state}
										</Typography>
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
