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
	date: Date;
	icon: React.ReactNode;
	children?: React.ReactNode;
	variant?: 'compact';
}

const TimelineNodeBox = styled(Box)(() => ({
	'&:first-child': {
		'& .MuiDivider-vertical.first': {
			display: 'block',
		},
	},
	'&:last-child': {
		'& .MuiDivider-vertical.last': {
			display: 'none',
		},
	},
}));

export function TimelineNode(props: TimelineNodeProps) {
	const { title, date, icon, children, variant } = props;
	const { palette } = useTheme();

	return (
		<TimelineNodeBox sx={{ display: 'flex', mb: 1 }}>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignContent: 'center',
					mr: 1,
					minHeight: '50px',
					minWidth: '30px',
				}}
			>
				{variant === 'compact' ? (
					icon
				) : (
					<Avatar
						sx={{
							width: '30px',
							height: '30px',
							backgroundColor: palette.brand.accentLight,
						}}
					>
						{icon}
					</Avatar>
				)}
				<Divider
					className='last'
					orientation='vertical'
					sx={{
						mt: 1,
						flex: 1,
						width: 'calc(50% + 1px)',
						borderRightWidth: '2px',
					}}
				/>
			</Box>

			{variant === 'compact' && (
				<Box
					sx={{
						width: '100%',
						display: 'flex',
						pt: 0.5,
						alignItems: 'flex-start',
					}}
				>
					<Box sx={{ flex: 1 }}>
						<Typography variant='subtitle2'>{title}</Typography>
					</Box>
					<Typography variant='caption'>
						{date?.toLocaleDateString()}
					</Typography>
				</Box>
			)}
			{variant !== 'compact' && (
				<Card sx={{ flex: 1, mb: 2 }} variant='outlined'>
					<Toolbar
						disableGutters
						sx={{
							height: '30px',
							minHeight: '30px',
							px: 1,
							display: 'flex',
						}}
						variant='dense'
					>
						<Box sx={{ flex: 1 }}>
							<Typography variant='overline'>{title}</Typography>
						</Box>
						<Typography variant='caption'>
							{date?.toLocaleDateString()}
						</Typography>
					</Toolbar>
					{children && <Box sx={{ p: 1 }}>{children}</Box>}
				</Card>
			)}
		</TimelineNodeBox>
	);
}
