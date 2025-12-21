'use client';

import { Checkbox, Chip } from '@mui/material';
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
				<Chip
					color={
						appropriation.amount === 0
							? 'default'
							: appropriation.amount > 0
								? 'error'
								: 'success'
					}
					label={new Intl.NumberFormat('en-US', {
						style: 'currency',
						currency: 'USD',
					}).format(appropriation.amount ?? 0)}
					size='small'
				/>
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
			renderCell: ({ row: appropriation }) =>
				appropriation.fiscal_years.join(', '),
		},
		{
			field: 'until_expended',
			headerName: 'Until Expended',
			editable: false,
			renderCell: ({ row: appropriation }) => (
				<Checkbox checked={appropriation.until_expended ?? false} />
			),
		},
		{
			field: 'new_spending',
			headerName: 'New Spending',
			editable: false,
			renderCell: ({ row: appropriation }) => (
				<Checkbox checked={appropriation.new_spending ?? false} />
			),
		},
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
