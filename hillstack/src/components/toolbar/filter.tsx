import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import Button from '@mui/material/Button';
import React from 'react';

import type { ToolbarFilterOption } from '~/types/components';
import { ToolbarFilterMenu } from './filterMenu';

export interface ToolbarFilterProps<T> {
	title: string;
	prop: string;
	value: ToolbarFilterOption<T>[] | undefined;
	options: ToolbarFilterOption<T>[];
	multiSelect: boolean;
	searchable?: boolean;
	onTagChange: (
		tag: string,
		value: ToolbarFilterOption<T>[] | undefined,
	) => void;
}

export function ToolbarFilter<T>({
	title,
	prop,
	value,
	options,
	onTagChange,
	multiSelect,
	searchable,
}: ToolbarFilterProps<T>) {
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
				{title}
			</Button>
			<ToolbarFilterMenu
				anchor={anchorElNav}
				multiSelect={multiSelect}
				onClose={handleCloseNavMenu}
				onSelect={onTagChange}
				options={options}
				prop={prop}
				searchable={searchable}
				title={title}
				value={value}
			/>
		</>
	);
}
