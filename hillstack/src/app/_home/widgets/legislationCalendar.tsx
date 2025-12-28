'use client';

import { Box, Tooltip, Typography } from '@mui/material';
import {
	eachDayOfInterval,
	endOfYear,
	format,
	getDay,
	startOfYear,
} from 'date-fns';
import type React from 'react';
import { useEffect, useRef, useState } from 'react';
import { api } from '~/trpc/react';
import { DashboardWidgetContent } from './';

type HeatmapProps = {
	data: { date: string | undefined; count: number }[];
};

const HeatmapCalendar: React.FC<HeatmapProps> = ({ data }) => {
	const containerRef = useRef<HTMLDivElement>(null);
	const [squareSize, setSquareSize] = useState(12); // default

	// Update square size based on container width
	useEffect(() => {
		const updateSize = () => {
			if (!containerRef.current) return;
			const containerWidth = containerRef.current.offsetWidth;
			const maxWeeks = 53;
			const spacing = 4; // margin between squares
			const availableWidth = containerWidth - 20; // padding for weekday labels
			const size = Math.floor(
				(availableWidth - maxWeeks * spacing) / maxWeeks,
			);
			setSquareSize(Math.max(size, 4)); // minimum 4px
		};

		updateSize();
		window.addEventListener('resize', updateSize);
		return () => window.removeEventListener('resize', updateSize);
	}, []);

	const heatmapMap = new Map(data.map((item) => [item.date, item.count]));

	const yearStart = startOfYear(new Date());
	const yearEnd = endOfYear(new Date());
	const allDays = eachDayOfInterval({ start: yearStart, end: yearEnd });

	const colorScale = (count: number) => {
		if (!count) return '#ebedf022';
		if (count < 10) return '#9be9a8';
		if (count < 20) return '#40c463';
		return '#30a14e';
	};

	const firstWeekday = getDay(yearStart);

	// Split days into weeks
	const weeks: (Date | null)[][] = [];
	let week: (Date | null)[] = Array(firstWeekday).fill(null);
	allDays.forEach((day) => {
		week.push(day);
		if (week.length === 7) {
			weeks.push(week);
			week = [];
		}
	});
	if (week.length > 0) {
		while (week.length < 7) week.push(null);
		weeks.push(week);
	}

	// Determine first week index for each month
	const monthPositions: { [month: string]: number } = {};
	weeks.forEach((weekDays, weekIndex) => {
		for (const day of weekDays) {
			if (!day) continue;
			const month = format(day, 'MMM');
			if (!(month in monthPositions)) {
				monthPositions[month] = weekIndex;
			}
		}
	});

	const weekdayLabels = ['S', 'M', 'T', 'W', 'Th', 'F', 'Sa'];

	return (
		<Box
			overflow='hidden'
			ref={containerRef}
			sx={{
				height: '200px',
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
			}}
			width='100%'
		>
			<Box display='flex'>
				{/* Weekday labels */}
				<Box display='flex' flexDirection='column' mr={1} mt={3.25}>
					{weekdayLabels.map((day) => (
						<Typography
							key={day}
							sx={{
								height: squareSize,
								mb: 0.5,
								fontSize: squareSize * 0.6,
							}}
							variant='caption'
						>
							{day}
						</Typography>
					))}
				</Box>

				<Box>
					{/* Month labels */}
					<Box display='flex' mb={0.5}>
						{weeks.map((_, weekIndex) => {
							const monthLabel = Object.entries(
								monthPositions,
							).find(([, idx]) => idx === weekIndex);
							return (
								<Box
									key={weekIndex}
									mr={0.5}
									width={squareSize}
								>
									{monthLabel && (
										<Typography
											sx={{
												fontSize: Math.max(
													squareSize * 0.6,
													8,
												),
											}}
											variant='caption'
										>
											{monthLabel[0]}
										</Typography>
									)}
								</Box>
							);
						})}
					</Box>

					{/* Heatmap squares */}
					<Box display='flex'>
						{weeks.map((weekDays, weekIndex) => (
							<Box
								display='flex'
								flexDirection='column'
								key={weekIndex}
								mr={0.5}
							>
								{weekDays.map((day, dayIndex) => {
									if (!day)
										return (
											<Box
												height={squareSize}
												key={dayIndex}
												mb={0.5}
												width={squareSize}
											/>
										);
									const dateStr = format(day, 'yyyy-MM-dd');
									const count = heatmapMap.get(dateStr) || 0;
									return (
										<Tooltip
											key={dayIndex}
											title={`${dateStr}: ${count}`}
										>
											<Box
												bgcolor={colorScale(count)}
												borderRadius={2}
												height={squareSize}
												mb={0.5}
												width={squareSize}
											/>
										</Tooltip>
									);
								})}
							</Box>
						))}
					</Box>
				</Box>
			</Box>
		</Box>
	);
};

export function LegislationCalendar() {
	const { data, isLoading, isError } = api.stats.calendar.useQuery();

	return (
		<DashboardWidgetContent isError={isError} isLoading={isLoading}>
			{data && <HeatmapCalendar data={data} />}
		</DashboardWidgetContent>
	);
}
