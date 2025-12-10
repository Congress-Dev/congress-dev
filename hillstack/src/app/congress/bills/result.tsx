import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import type { inferRouterOutputs } from '@trpc/server';
import Link from 'next/link';
import type { AppRouter } from '~/server/api/root';

export interface BillSearchResultProps {
	bill: inferRouterOutputs<AppRouter>['bill']['search']['legislation'][0];
}

export function BillSearchResult({ bill }: BillSearchResultProps) {
	const legislator = bill.legislation_sponsorship[0]?.legislator;

	return (
		<>
			<ListItem component='div' disablePadding>
				<ListItemButton>
					<ListItemText
						primary={
							<Link
								href={`/congress/bills/${bill.legislation_id}`}
								style={{ width: '100%', display: 'block' }}
							>
								<Typography color='primary' variant='h4'>
									{bill.title}
								</Typography>
								<Typography variant='caption'>
									{`${bill.congress?.session_number}th - `}
									{bill.chamber === 'House' ? 'H.R' : 'S'}
									{'. #'}
									{bill.number}
									{' by '}
									{`${legislator?.first_name} ${legislator?.last_name}`}
								</Typography>
							</Link>
						}
					/>
				</ListItemButton>
			</ListItem>
			<Divider />
		</>
	);
}
