import CloseIcon from "@mui/icons-material/Close";
import { Radio } from "@mui/material";
import Box from "@mui/material/Box";
import Checkbox from "@mui/material/Checkbox";
import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import MenuList from "@mui/material/MenuList";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import { useEffect, useMemo, useRef, useState } from "react";

import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";
import type { ToolbarFilterOption } from "~/types/components";

export interface ToolbarSortMenuProps<T> {
    title: string;
    prop: T | null;
    direction: 'asc' | 'desc';
    options: ToolbarFilterOption<T>[];
    anchor: HTMLElement | null;
    onClose: () => void;
    onSelect: (
        property: T,
		direction: 'asc' | 'desc'
    ) => void;
}

export function ToolbarSortMenu<T>({
    prop,
    value,
    options,
    anchor,
    onClose,
    onSelect,
}: ToolbarSortMenuProps<T>) {
    const open = Boolean(anchor);
    const inputRef = useRef<HTMLElement>(null);
    const [property, setProperty] = useState<T | null>(null);
    const [direction, setDirection] = useState("desc");

	useEffect(() => {
		if(property) {
			onSelect(property, direction);
		}
	}, [property, direction])
    // const [query, setQuery] = useState('');
    // const availableOptions = useMemo(() => {
    // 	return options
    // 		.filter(
    // 			(option) =>
    // 				query === '' ||
    // 				(query !== '' &&
    // 					option.label
    // 						.toLowerCase()
    // 						.includes(query.toLowerCase())),
    // 		)
    // 		.sort((a, b) => {
    // 			if (a.label < b.label) return -1;
    // 			if (a.label > b.label) return 1;
    // 			return 0;
    // 		});
    // }, [options, query]);

    // const handleSelect = (
    // 	prop: string,
    // 	selection: ToolbarFilterOption<T> | undefined,
    // ) => {
    // 	if (!selection) {
    // 		return;
    // 	}

    // 	const match =
    // 		value?.find((val) => val.value === selection.value) ?? null;
    // 	if (match) {
    // 		const newValue = value?.filter(
    // 			(val) => val.value !== selection.value,
    // 		);
    // 		onSelect(prop, newValue?.length ? newValue : undefined);
    // 	} else {
    // 		if (multiSelect) {
    // 			onSelect(prop, [...(value ?? []), selection]);
    // 		} else {
    // 			onSelect(prop, [selection]);
    // 		}
    // 	}
    // };

    useEffect(() => {
        if (open && inputRef.current) {
            inputRef.current.focus();
        }
    }, [open]);

    return (
        <Menu
            anchorEl={anchor}
            anchorOrigin={{
                vertical: "bottom",
                horizontal: "right",
            }}
            disableAutoFocus
            disableAutoFocusItem
            id="menu-appbar"
            keepMounted
            onClose={onClose}
            open={Boolean(anchor)}
            slotProps={{
                list: {
                    sx: { py: 0 },
                },
            }}
            sx={{ display: "block" }}
            transformOrigin={{
                vertical: "top",
                horizontal: "right",
            }}
        >
            <Box
                sx={{
                    display: "flex",
                    p: 0,
                    px: 1,
                    m: 0,
                    my: 0.5,
                    alignContent: "top",
                }}
            >
                <Typography
                    noWrap
                    sx={{
                        mr: 2,
                        flexGrow: 1,
                        lineHeight: "28px",
                    }}
                    variant="subtitle2"
                >
                    Sort by
                </Typography>

                <IconButton onClick={onClose} size="small">
                    <CloseIcon fontSize="inherit" />
                </IconButton>
            </Box>
            <Divider sx={{ mt: 1, mb: 1 }} />
            <MenuList dense sx={{ py: 0 }}>
                {options.map((option) => (
                    <MenuItem
                        key={option.label}
                        onClick={() => setProperty(option.value)}
                        sx={{
                            backgroundColor: (theme) =>
                                property === option.value
                                    ? theme.palette.brand.accent
                                    : "none",
                        }}
                    >
                        <ListItemIcon>
                            <Radio
                                checked={
                                    property === option.value
                                }
                                size="small"
                                sx={{ px: 0, py: 0 }}
                            />
                        </ListItemIcon>
                        {option.label}
                    </MenuItem>
                ))}
            </MenuList>
            <Divider sx={{ mt: 1 }} />
            <MenuList dense>
                <MenuItem
                    onClick={() => setDirection("asc")}
                    sx={{
                        backgroundColor: (theme) =>
                            direction === "asc"
                                ? theme.palette.brand.accent
                                : "none",
                    }}
                >
                    <ListItemIcon>
                        <ArrowUpwardIcon />
                    </ListItemIcon>
                    Ascending
                </MenuItem>
                <MenuItem
                    onClick={() => setDirection("desc")}
                    sx={{
                        backgroundColor: (theme) =>
                            direction === "desc"
                                ? theme.palette.brand.accent
                                : "none",
                    }}
                >
                    <ListItemIcon>
                        <ArrowDownwardIcon />
                    </ListItemIcon>
                    Descending
                </MenuItem>
            </MenuList>
        </Menu>
    );
}
