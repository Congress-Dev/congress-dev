import { Prisma } from 'generated/prisma/client';
import { legislationchamber } from 'generated/prisma/enums';
import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const committeeRouter = createTRPCRouter({
	get: publicProcedure
		.input(
			z.object({
				id: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const committee =
				await ctx.db.legislation_committee.findUniqueOrThrow({
					where: {
						legislation_committee_id: input.id,
					},
				});

			const subcommittees = await ctx.db.legislation_committee.findMany({
				where: {
					parent_id: input.id,
					legislation_committee_id: { not: input.id },
				},
			});

			const legislation = await ctx.db.legislation.findMany({
				select: {
					legislation_id: true,
					title: true,
					number: true,
					chamber: true,
					congress: {
						select: {
							session_number: true,
						},
					},
					legislation_action: {
						select: {
							text: true,
						},
					},
				},
				where: {
					legislation_action: {
						some: {
							text: {
								contains: committee.name,
								mode: Prisma.QueryMode.insensitive,
							},
						},
					},
				},
				take: 10,
			});

			return {
				...committee,
				subcommittees,
				legislation,
			};
		}),
	search: publicProcedure
		.input(
			z.object({
				query: z.optional(z.string()),
				congress: z.optional(z.array(z.number())),
				chamber: z.optional(z.array(z.nativeEnum(legislationchamber))),
				committeeType: z.optional(z.array(z.string())),
				page: z.number(),
				pageSize: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { query, congress, chamber, committeeType, page, pageSize } =
				input;

			const where = {
				...(committeeType
					? { committee_type: { in: committeeType } }
					: {}),
				...(congress
					? { congress: { session_number: { in: congress } } }
					: {}),
				...(chamber ? { chamber: { in: chamber } } : {}),
				...(query
					? {
							name: {
								contains: query,
								mode: Prisma.QueryMode.insensitive,
							},
						}
					: {}),
			};

			const totalResults = await ctx.db.legislation_committee.count({
				where,
			});

			const committees = await ctx.db.legislation_committee.findMany({
				select: {
					name: true,
					legislation_committee_id: true,
					congress_id: true,
					thomas_id: true,
					chamber: true,
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
