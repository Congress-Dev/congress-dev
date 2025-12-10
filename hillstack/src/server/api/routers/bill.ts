import { Prisma } from 'generated/prisma/client';
import { legislationchamber } from 'generated/prisma/enums';
import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const billRouter = createTRPCRouter({
	get: publicProcedure
		.input(
			z.object({
				id: z.number(),
				version: z.optional(z.number()),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { id, version } = input;

			const bill = await ctx.db.legislation.findUniqueOrThrow({
				select: {
					title: true,
					number: true,
					chamber: true,
					legislation_version: {
						select: {
							legislation_version: true,
							effective_date: true,
							legislation_content: {
								select: {
									heading: true,
									content_str: true,
									content_type: true,
									section_display: true,
									parent_id: true,
									order_number: true,
									legislation_content_id: true,
									legislation_content_summary: {
										select: {
											summary: true,
										},
										orderBy: {
											legislation_content_id: 'asc',
										},
									},
								},
								orderBy: [
									{
										parent_id: 'asc',
									},
									{
										order_number: 'asc',
									},
								],
							},
							legislation_version_tag: {
								select: {
									tags: true,
								},
							},
						},
						where: {
							...(version && { legislation_version_id: version }),
						},
					},
					legislation_sponsorship: {
						select: {
							cosponsor: true,
							legislator: {
								select: {
									first_name: true,
									last_name: true,
									party: true,
									image_url: true,
									bioguide_id: true,
									job: true,
								},
							},
						},
					},
					legislation_vote: {
						select: {
							id: true,
							question: true,
							independent: true,
							republican: true,
							democrat: true,
							total: true,
							passed: true,
							chamber: true,
						},
					},
					legislative_policy_area_association: {
						select: {
							legislative_policy_area: {
								select: {
									name: true,
								},
							},
						},
					},
				},
				where: { legislation_id: id },
			});

			return bill;
		}),
	search: publicProcedure
		.input(
			z.object({
				congress: z.optional(z.array(z.number())),
				chamber: z.optional(z.array(z.nativeEnum(legislationchamber))),
				versions: z.optional(z.array(z.string())),
				query: z.optional(z.string()),
				page: z.number(),
				pageSize: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { query, congress, chamber, page, pageSize } = input;

			const titleClause = query
				? {
						title: {
							contains: query,
							mode: Prisma.QueryMode.insensitive,
						},
					}
				: {};
			const congressClause = congress
				? { congress: { session_number: { in: congress } } }
				: {};
			const chamberClause = chamber ? { chamber: { in: chamber } } : {};

			const where = {
				...titleClause,
				...congressClause,
				...chamberClause,
			};

			const totalResults = await ctx.db.legislation.count({
				where,
			});

			const legislation = await ctx.db.legislation.findMany({
				select: {
					legislation_id: true,
					chamber: true,
					number: true,
					title: true,
					policy_areas: true,
					legislation_version: {
						select: {
							legislation_version_id: true,
							legislation_version: true,
							effective_date: true,
						},
						orderBy: {
							legislation_version_id: 'asc',
						},
					},
					legislation_sponsorship: {
						select: {
							legislator: {
								select: {
									first_name: true,
									last_name: true,
									party: true,
									image_url: true,
								},
							},
						},
					},
					congress: {
						select: {
							session_number: true,
						},
					},
				},
				where,
				orderBy: {
					number: 'asc',
				},
				skip: (page - 1) * pageSize,
				take: pageSize,
			});

			return {
				legislation,
				totalResults,
			};
		}),
});
