import { Box } from '@mui/material';
import { RadarChart } from '@mui/x-charts';
import type React from 'react';
import { api } from '~/trpc/react';

type TagRadarChartProps = {
	data: {
		metrics: string[];
		counts: number[];
	};
};

const TagRadarChart: React.FC<TagRadarChartProps> = ({ data }) => {
	const maxValue = Math.max(...data.counts);

	return (
		<Box>
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
	const { data } = api.stats.tagRadar.useQuery();

	return data ? <TagRadarChart data={data} /> : <>Loading</>;
}
