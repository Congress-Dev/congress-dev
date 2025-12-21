'use client';

import type { SvgIconComponent } from '@mui/icons-material';
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
	icon: SvgIconComponent;
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
	const { title, date, icon: Icon, children, variant } = props;
	const { palette } = useTheme();

	return (
		<TimelineNodeBox sx={{ display: 'flex', mb: 0.5 }}>
			<Box
				sx={{
					display: 'flex',
					flexDirection: 'column',
					alignContent: 'center',
					mr: 1,
					minHeight: '40px',
					minWidth: '30px',
				}}
			>
				{variant === 'compact' ? (
					<Box sx={{ ml: '3px' }}>
						<Icon color='disabled' />
					</Box>
				) : (
					<Avatar
						sx={{
							width: '30px',
							height: '30px',
							backgroundColor: palette.brand.accentLight,
						}}
					>
						<Icon />
					</Avatar>
				)}
				<Divider
					className='last'
					orientation='vertical'
					sx={{
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
						alignItems: 'flex-start',
						pb: 2,
					}}
				>
					<Box sx={{ flex: 1 }}>
						<Typography sx={{ fontSize: '14px' }} variant='caption'>
							{title}
						</Typography>
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
