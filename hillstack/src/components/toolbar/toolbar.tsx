import AllInboxIcon from '@mui/icons-material/AllInbox';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import MuiToolbar from '@mui/material/Toolbar';
import type React from 'react';

export { ToolbarFilter } from './filter';

export interface ToolbarProps {
	results: number;
	filters: React.ReactNode;
	sorter?: React.ReactNode;
}

export function Toolbar({ results, filters, sorter }: ToolbarProps) {
	return (
		<MuiToolbar disableGutters variant='dense'>
			<AllInboxIcon sx={{ mr: 1 }} />
			{results.toLocaleString()} Results
			<Divider flexItem orientation='vertical' sx={{ mx: 2 }} />
			<Box
				sx={{
					display: 'flex',
					flexGrow: 1,
					justifyContent: 'flex-end',
				}}
			>
				{filters} {sorter}
			</Box>
		</MuiToolbar>
	);
}
