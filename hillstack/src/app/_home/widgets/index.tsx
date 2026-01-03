import ErrorIcon from '@mui/icons-material/Error';
import InboxIcon from '@mui/icons-material/Inbox';
import { Box, CircularProgress, Typography } from '@mui/material';
import type React from 'react';

function DashboardWidgetState({ children }: { children?: React.ReactNode }) {
	return (
		<Box
			sx={{
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				height: 220,
			}}
		>
			{children}
		</Box>
	);
}

export function DashboardWidgetLoading() {
	return (
		<DashboardWidgetState>
			<CircularProgress />
		</DashboardWidgetState>
	);
}

export function DashboardWidgetError() {
	return (
		<DashboardWidgetState>
			<ErrorIcon color='disabled' sx={{ mr: 2 }} />
			<Typography color='textDisabled' variant='h2'>
				Error Loading
			</Typography>
		</DashboardWidgetState>
	);
}

export function DashboardWidgetNoContent() {
	return (
		<DashboardWidgetState>
			<InboxIcon color='disabled' sx={{ mr: 2 }} />
			<Typography color='textDisabled' variant='h2'>
				No Content
			</Typography>
		</DashboardWidgetState>
	);
}

export function DashboardWidgetContent({
	isLoading,
	isError,
	isEmpty,
	children,
}: {
	isLoading: boolean;
	isError: boolean;
	isEmpty: boolean;
	children?: React.ReactNode;
}) {
	if (isLoading) {
		return <DashboardWidgetLoading />;
	}

	if (isError) {
		return <DashboardWidgetError />;
	}

	if (isEmpty) {
		return <DashboardWidgetNoContent />;
	}

	return children;
}
