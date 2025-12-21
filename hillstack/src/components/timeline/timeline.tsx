'use client';

import { Timeline as MUITimeline } from '@mui/lab';
import {
	Avatar,
	Box,
	Card,
	Toolbar,
	Typography,
	useTheme,
} from '@mui/material';
import { Children } from 'react';

interface TimelineProps {
	title: string;
	content: string | null | undefined;
	icon: React.ReactNode;
	children: React.ReactNode;
}

export function Timeline(props: TimelineProps) {
	const { title, content, icon, children } = props;
	const { palette } = useTheme();

	const sortedChildren = Children.toArray(children);
	sortedChildren.sort((a, b) => {
		// @ts-expect-error
		return a.props.date - b.props.date;
	});

	return (
		<>
			<Box sx={{ display: 'flex' }}>
				<Avatar
					sx={{
						width: '40px',
						height: '40px',
						mr: 1,
						backgroundColor: palette.brand.accentLight,
						display: { xs: 'none', md: 'flex' },
					}}
				>
					{icon}
				</Avatar>
				<Card sx={{ flex: 1 }} variant='outlined'>
					<Toolbar
						disableGutters
						sx={{
							height: '40px',
							minHeight: '40px',
							px: 2,
						}}
						variant='dense'
					>
						<Typography variant='subtitle2'>{title}</Typography>
					</Toolbar>
					<Box sx={{ p: 2 }}>{content}</Box>
				</Card>
			</Box>
			<MUITimeline
				position='right'
				sx={{
					pl: { xs: 0, md: 6 },
					pr: 0,
					'& .MuiTimelineItem-root:before': { flex: 0, padding: 0 },
				}}
			>
				{sortedChildren}
			</MUITimeline>
		</>
	);
}
