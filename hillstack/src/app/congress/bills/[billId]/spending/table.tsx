'use client';

import AddCardIcon from '@mui/icons-material/AddCard';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';
import { Box, Tooltip, Typography } from '@mui/material';
import { DataGrid, type GridColDef, type GridRowsProp } from '@mui/x-data-grid';

interface Appropriation {
	id: number;
	amount: number;
	purpose: string | null;
	fiscal_years: number[];
	until_expended: boolean;
	new_spending: boolean;
	appropriation_id: number;
}

export default function BillSpendingTable({
	rows,
}: {
	rows: GridRowsProp<Appropriation>;
}) {
	const columns: GridColDef[] = [
		{
			field: 'amount',
			headerName: 'Amount',
			editable: false,
			type: 'number',
			width: 200,
			renderCell: ({ row: appropriation }) => (
				<Typography
					color={
						appropriation.amount === 0
							? 'default'
							: appropriation.amount > 0
								? 'error'
								: 'success'
					}
					variant='subtitle1'
				>
					{new Intl.NumberFormat('en-US', {
						style: 'currency',
						currency: 'USD',
					}).format(appropriation.amount ?? 0)}
				</Typography>
			),
		},
		{
			field: 'purpose',
			headerName: 'Description',
			editable: false,
			flex: 1,
		},
		{
			field: 'fiscal_years',
			headerName: 'Fiscal Years',
			editable: false,
			width: 400,
			renderCell: ({ row: appropriation }) =>
				appropriation.fiscal_years.join(', '),
		},
		{
			field: 'Tags',
			headerName: 'Tags',
			editable: false,
			width: 80,
			renderCell: ({ row: appropriation }) => (
				<Box
					sx={{
						display: 'flex',
						alignItems: 'center',
						gap: 1,
						height: '100%',
					}}
				>
					{appropriation.until_expended && (
						<Tooltip title='Until Expended'>
							<MoneyOffIcon />
						</Tooltip>
					)}
					{appropriation.new_spending && (
						<Tooltip title='New Spending'>
							<AddCardIcon />
						</Tooltip>
					)}
				</Box>
			),
		},
		// {
		// 	field: 'until_expended',
		// 	headerName: 'Until Expended',
		// 	editable: false,
		// 	renderCell: ({ row: appropriation }) => (
		// 		<Checkbox checked={appropriation.until_expended ?? false} />
		// 	),
		// },
		// {
		// 	field: 'new_spending',
		// 	headerName: 'New Spending',
		// 	editable: false,
		// 	renderCell: ({ row: appropriation }) => (
		// 		<Checkbox checked={appropriation.new_spending ?? false} />
		// 	),
		// },
	];

	return (
		<DataGrid
			columns={columns}
			disableRowSelectionOnClick
			rowHeight={35}
			rows={rows}
		/>
	);
}
