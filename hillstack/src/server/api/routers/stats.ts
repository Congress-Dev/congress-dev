import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const statsRouter = createTRPCRouter({
	tagRadar: publicProcedure.query(async ({ ctx }) => {
		const versions = await ctx.db.legislation.findMany({
			select: {
				legislation_version: {
					select: {
						legislation_version_tag: {
							select: {
								tags: true,
							},
						},
					},
					orderBy: {
						effective_date: 'desc',
					},
					take: 1,
				},
			},
		});

		const allTags = versions.flatMap((v) =>
			v.legislation_version.flatMap((lv) =>
				lv.legislation_version_tag.flatMap((t) => t.tags),
			),
		);

		const tagCount: Record<string, number> = {};
		allTags.forEach((tag) => {
			tagCount[tag] = (tagCount[tag] || 0) + 1;
		});

		const topTags = Object.entries(tagCount)
			.sort((a, b) => b[1] - a[1])
			.slice(0, 5);

		return {
			metrics: topTags.map(([tag]) => tag),
			counts: topTags.map(([_, count]) => count),
		};
	}),
	calendar: publicProcedure.query(async ({ ctx }) => {
		const startOfYear = new Date(new Date().getFullYear(), 0, 1);
		const endOfYear = new Date(new Date().getFullYear() + 1, 0, 1);

		const data = await ctx.db.legislation_version.groupBy({
			by: ['effective_date'],
			_count: {
				legislation_version_id: true,
			},
			orderBy: {
				effective_date: 'asc',
			},
			where: {
				effective_date: {
					gte: startOfYear,
					lt: endOfYear,
				},
			},
		});

		const heatmapData = data.map((item) => ({
			date: item.effective_date?.toISOString().split('T')[0],
			count: item._count.legislation_version_id,
		}));

		return heatmapData;
	}),
});
