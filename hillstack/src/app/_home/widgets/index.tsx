import ErrorIcon from '@mui/icons-material/Error';
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
			<ErrorIcon sx={{ mr: 2 }} />
			<Typography variant='h2'>Error Loading</Typography>
		</DashboardWidgetState>
	);
}

export function DashboardWidgetContent({
	isLoading,
	isError,
	children,
}: {
	isLoading: boolean;
	isError: boolean;
	children?: React.ReactNode;
}) {
	if (isLoading) {
		return <DashboardWidgetLoading />;
	}

	if (isError) {
		return <DashboardWidgetError />;
	}

	return children;
}
