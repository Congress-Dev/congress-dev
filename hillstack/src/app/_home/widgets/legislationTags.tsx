import { Box } from '@mui/material';
import { RadarChart } from '@mui/x-charts';
import type React from 'react';
import { api } from '~/trpc/react';
import { DashboardWidgetContent } from './';

type TagRadarChartProps = {
	data: {
		metrics: string[];
		counts: number[];
	};
};

const TagRadarChart: React.FC<TagRadarChartProps> = ({ data }) => {
	const maxValue = Math.max(...data.counts);

	return (
		<Box sx={{ px: 3, pt: 1, pb: 2 }}>
			<RadarChart
				height={200}
				radar={{
					max: maxValue,
					metrics: data.metrics,
				}}
				series={[{ data: data.counts }]}
				shape='circular'
			/>
		</Box>
	);
};

export default TagRadarChart;

export function LegislationTags() {
	const { data, isLoading, isError } = api.stats.tagRadar.useQuery();

	return (
		<DashboardWidgetContent
			isEmpty={data?.counts?.length === 0}
			isError={isError}
			isLoading={isLoading}
		>
			{data && <TagRadarChart data={data} />}
		</DashboardWidgetContent>
	);
}
