'use client';

import type { SvgIconComponent } from '@mui/icons-material';
import {
	TimelineConnector,
	TimelineContent,
	TimelineItem,
	TimelineSeparator,
} from '@mui/lab';
import {
	Box,
	Card,
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

const TimelineNodeBox = styled(TimelineItem)(() => ({
	'&:last-child': {
		'& .MuiTimelineConnector-root': {
			display: 'none',
		},
	},
}));

export function TimelineNode(props: TimelineNodeProps) {
	const { title, date, icon: Icon, children, variant } = props;
	const { palette } = useTheme();

	return (
		<TimelineNodeBox sx={{ minHeight: '25px', mt: 1 }}>
			<TimelineSeparator sx={{ mt: 0, width: '30px' }}>
				<Box
					sx={{
						color:
							variant === 'compact'
								? palette.action.disabled
								: palette.brand.accentLight,
					}}
				>
					<Icon />
				</Box>
				<TimelineConnector sx={{ mt: 0, bgcolor: 'divider' }} />
			</TimelineSeparator>
			<TimelineContent sx={{ pr: 0, pt: 0 }}>
				{variant === 'compact' ? (
					<Box
						sx={{
							width: '100%',
							display: 'flex',
							alignItems: 'flex-start',
							pb: 1,
						}}
					>
						<Box sx={{ flex: 1 }}>
							<Typography
								sx={{ fontSize: '14px' }}
								variant='caption'
							>
								{title}
							</Typography>
						</Box>
						<Typography variant='caption'>
							{date?.toLocaleDateString()}
						</Typography>
					</Box>
				) : (
					<Card sx={{ flex: 1, mb: 2 }} variant='outlined'>
						<Toolbar
							disableGutters
							sx={{
								minHeight: '30px',
								px: 1,
								display: 'flex',
							}}
							variant='dense'
						>
							<Box sx={{ flex: 1 }}>
								<Typography variant='overline'>
									{title}
								</Typography>
							</Box>
							<Typography variant='caption'>
								{date?.toLocaleDateString()}
							</Typography>
						</Toolbar>
						{children && <Box sx={{ p: 1 }}>{children}</Box>}
					</Card>
				)}
			</TimelineContent>
		</TimelineNodeBox>
	);
}
