import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const committeeRouter = createTRPCRouter({
	search: publicProcedure
		.input(
			z.object({
				query: z.optional(z.string()),
				congress: z.optional(z.array(z.string())),
				chamber: z.optional(z.array(z.string())),
				committeeType: z.optional(z.array(z.string())),
				page: z.number(),
				pageSize: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { committeeType, page, pageSize } = input;

			const where = {
				...(committeeType
					? { committee_type: { in: committeeType } }
					: {}),
			};

			const totalResults = await ctx.db.legislation_committee.count({
				where,
			});

			const committees = await ctx.db.legislation_committee.findMany({
				select: {
					name: true,
					legislation_committee_id: true,
				},
				where,
				orderBy: { name: 'asc' },
				skip: (page - 1) * pageSize,
				take: pageSize,
			});

			return {
				committees,
				totalResults,
			};
		}),
});
