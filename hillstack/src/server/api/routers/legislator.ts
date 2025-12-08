import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const legislatorRouter = createTRPCRouter({
	search: publicProcedure
		.input(
			z.object({
				query: z.optional(z.string()),
				congress: z.optional(z.array(z.string())),
				chamber: z.optional(z.array(z.string())),
				page: z.number(),
				pageSize: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { page, pageSize } = input;
			const where = {};

			const totalResults = await ctx.db.legislator.count({
				where,
			});

			const members = await ctx.db.legislator.findMany({
				select: {
					first_name: true,
					last_name: true,
					party: true,
					state: true,
					district: true,
					image_url: true,
					bioguide_id: true,
					job: true,
				},
				where,
				orderBy: [{ last_name: 'asc' }, { first_name: 'asc' }],
				skip: (page - 1) * pageSize,
				take: pageSize,
			});

			return {
				members,
				totalResults,
			};
		}),
});
