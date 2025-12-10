'use client';

import {
	Avatar,
	Box,
	Card,
	Divider,
	styled,
	Toolbar,
	Typography,
	useTheme,
} from '@mui/material';
import type React from 'react';

interface TimelineNodeProps {
	title: string;
	icon: React.ReactNode;
	children: React.ReactNode;
}

const TimelineNodeBox = styled(Box)(() => ({
	'&:last-child': {
		'& .MuiDivider-vertical': {
			display: 'none',
		},
	},
}));

export function TimelineNode(props: TimelineNodeProps) {
	const { title, icon, children } = props;
	const { palette } = useTheme();

	return (
		<TimelineNodeBox sx={{ display: 'flex', mb: 1 }}>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignContent: 'center',
					mr: 1,
				}}
			>
				<Avatar
					sx={{
						width: '30px',
						height: '30px',
						backgroundColor: palette.brand.accentLight,
					}}
				>
					{icon}
				</Avatar>
				<Divider
					orientation='vertical'
					sx={{
						mt: 1,
						flex: 1,
						width: 'calc(50% + 1px)',
						borderRightWidth: '2px',
					}}
				/>
			</Box>
			<Card sx={{ flex: 1, mb: 2 }} variant='outlined'>
				<Toolbar
					disableGutters
					sx={{
						height: '30px',
						minHeight: '30px',
						px: 1,
					}}
					variant='dense'
				>
					<Typography variant='overline'>{title}</Typography>
				</Toolbar>
				<Box sx={{ p: 1 }}>{children}</Box>
			</Card>
		</TimelineNodeBox>
	);
}
