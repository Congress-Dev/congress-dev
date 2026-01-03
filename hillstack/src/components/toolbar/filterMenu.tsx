import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import Box from '@mui/material/Box';
import Checkbox from '@mui/material/Checkbox';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import MenuList from '@mui/material/MenuList';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useEffect, useMemo, useRef, useState } from 'react';

import type { ToolbarFilterOption } from '~/types/components';

export interface ToolbarFilterMenuProps<T> {
	title: string;
	prop: string;
	value: ToolbarFilterOption<T>[] | undefined;
	options: ToolbarFilterOption<T>[];
	multiSelect: boolean;
	anchor: HTMLElement | null;
	onClose: () => void;
	onSelect: (
		tag: string,
		value: ToolbarFilterOption<T>[] | undefined,
	) => void;
}

export function ToolbarFilterMenu<T>({
	title,
	prop,
	value,
	options,
	multiSelect = false,
	anchor,
	onClose,
	onSelect,
}: ToolbarFilterMenuProps<T>) {
	const open = Boolean(anchor);
	const inputRef = useRef<HTMLElement>(null);
	const [query, setQuery] = useState('');
	const availableOptions = useMemo(() => {
		return options
			.filter(
				(option) =>
					multiSelect === true ||
					value == null ||
					value?.find((val) => val.value !== option.value),
			)
			.filter(
				(option) =>
					query === '' ||
					(query !== '' &&
						option.label
							.toLowerCase()
							.includes(query.toLowerCase())),
			)
			.sort((a, b) => {
				if (a.label < b.label) return -1;
				if (a.label > b.label) return 1;
				return 0;
			});
	}, [value, options, query, multiSelect]);

	const handleSelect = (
		prop: string,
		selection: ToolbarFilterOption<T> | undefined,
	) => {
		if (!selection) {
			return;
		}

		const match =
			value?.find((val) => val.value === selection.value) ?? null;
		if (match) {
			const newValue = value?.filter(
				(val) => val.value !== selection.value,
			);
			onSelect(prop, newValue?.length ? newValue : undefined);
		} else {
			if (multiSelect) {
				onSelect(prop, [...(value ?? []), selection]);
			} else {
				onSelect(prop, [selection]);
			}
		}
	};

	useEffect(() => {
		if (open && inputRef.current) {
			inputRef.current.focus();
		}
	}, [open]);

	return (
		<Menu
			anchorEl={anchor}
			anchorOrigin={{
				vertical: 'bottom',
				horizontal: 'right',
			}}
			disableAutoFocus
			disableAutoFocusItem
			id='menu-appbar'
			keepMounted
			onClose={onClose}
			open={Boolean(anchor)}
			slotProps={{
				list: {
					sx: { py: 0 },
				},
			}}
			sx={{ display: 'block' }}
			transformOrigin={{
				vertical: 'top',
				horizontal: 'right',
			}}
		>
			<Box
				sx={{
					display: 'flex',
					p: 0,
					px: 1,
					m: 0,
					my: 0.5,
					alignContent: 'top',
				}}
			>
				<Typography
					noWrap
					sx={{
						mr: 2,
						flexGrow: 1,
						lineHeight: '28px',
					}}
					variant='subtitle2'
				>{`Filter by ${title.toLowerCase()}`}</Typography>

				<IconButton onClick={onClose} size='small'>
					<CloseIcon fontSize='inherit' />
				</IconButton>
			</Box>
			<Box sx={{ px: 1 }}>
				<TextField
					id='outlined-basic'
					inputRef={inputRef}
					onChange={(e) => setQuery(e.target.value)}
					onKeyDown={(e) => e.stopPropagation()}
					placeholder='Search'
					size='small'
					value={query}
					variant='outlined'
				/>
			</Box>
			<Divider sx={{ mt: 1 }} />
			{multiSelect === false && value && value[0] != null ? (
				<MenuList dense sx={{ py: 0 }}>
					<MenuItem onClick={() => handleSelect(prop, value[0])}>
						<ListItemIcon>
							<CheckIcon fontSize='inherit' />
						</ListItemIcon>
						{value[0].label}
					</MenuItem>
				</MenuList>
			) : null}
			{multiSelect === false && value && availableOptions.length > 0 ? (
				<Divider />
			) : null}
			<MenuList dense sx={{ py: 0 }}>
				{availableOptions.map((option) => (
					<MenuItem
						key={option.label}
						onClick={() => handleSelect(prop, option)}
					>
						{multiSelect === false ? (
							<ListItemIcon />
						) : (
							<ListItemIcon>
								<Checkbox
									checked={
										(Array.isArray(value) &&
											value.find(
												(val) =>
													val.value === option.value,
											) != null) ||
										false
									}
									size='small'
									sx={{ px: 0, py: 0 }}
								/>
							</ListItemIcon>
						)}
						{option.label}
					</MenuItem>
				))}
			</MenuList>
		</Menu>
	);
}
