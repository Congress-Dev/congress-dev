import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import Button from '@mui/material/Button';
import React from 'react';

import type { ToolbarFilterOption, ToolbarSortOption } from '~/types/components';
import { ToolbarSortMenu } from './sortMenu';

export interface ToolbarSortProps<T> {
	title: string;
	prop: string;
	value: ToolbarFilterOption<T>[] | undefined;
	options: ToolbarSortOption<T>[];
}

export function ToolbarSort<T>({
	title,
	prop,
	value,
	options,
}: ToolbarSortProps<T>) {
	const [anchorElNav, setAnchorElNav] = React.useState<null | HTMLElement>(
		null,
	);
	const handleOpenNavMenu = (event: React.MouseEvent<HTMLElement>) => {
		setAnchorElNav(event.currentTarget);
	};
	const handleCloseNavMenu = () => {
		setAnchorElNav(null);
	};

	return (
		<>
			<Button
				color='secondary'
				endIcon={<ArrowDropDownIcon />}
				onClick={handleOpenNavMenu}
			>
				Sort
			</Button>
			<ToolbarSortMenu
				anchor={anchorElNav}
				onClose={handleCloseNavMenu}
				options={options}
				prop={prop}
				title={title}
				value={value}
				onSelect={() => {}}
			/>
		</>
	);
}
