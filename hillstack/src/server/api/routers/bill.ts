import { Prisma } from 'generated/prisma/client';
import { legislationchamber } from 'generated/prisma/enums';
import { SortOrder } from 'generated/prisma/internal/prismaNamespace';
import { z } from 'zod';
import {
	buildNestedDiffTrees,
	mergeDiffTrees,
} from '~/server/api/helpers/bill';
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
							legislation_version_id: true,
							legislation_version: true,
							created_at: true,
							effective_date: true,
							legislation_content: {
								select: {
									legislation_content_summary: {
										select: {
											summary: true,
										},
										orderBy: {
											legislation_content_id: 'asc',
										},
									},
								},
								where: {
									content_type: 'legis-body',
								},
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
							datetime: true,
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
					legislation_action: {
						select: {
							legislation_action_id: true,
							action_date: true,
							action_type: true,
							action_code: true,
							text: true,
						},
						where: {
							text: { not: null },
							OR: [
								{
									action_type: {
										in: ['President'],
									},
								},
								{
									action_type: {
										in: ['Committee'],
									},
									text: {
										startsWith: 'Referred',
									},
								},
								{
									action_type: {
										in: ['IntroReferral'],
									},
									action_code: 'H11100',
								},
							],
						},
						distinct: ['text'],
					},
				},
				where: { legislation_id: id },
			});

			const signed = bill.legislation_action.find(
				(action) => action.action_code === 'E40000',
			);

			const latestVersion =
				bill.legislation_version[bill.legislation_version.length - 1];

			return {
				...bill,
				signed,
				latestVersion,
			};
		}),
	text: publicProcedure
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
					legislation_version: {
						select: {
							legislation_version: true,
							legislation_content: {
								select: {
									heading: true,
									content_str: true,
									content_type: true,
									section_display: true,
									parent_id: true,
									order_number: true,
									legislation_version_id: true,
									legislation_content_id: true,
									legislation_content_summary: {
										select: {
											summary: true,
										},
										orderBy: {
											legislation_content_id: 'asc',
										},
									},
									legislation_action_parse: {
										select: {
											actions: true,
											citations: true,
										},
									},
								},
								orderBy: [
									{ legislation_content_id: 'asc' },
									{ parent_id: 'asc' },
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
				},
				where: { legislation_id: id },
			});

			const latestVersion =
				bill.legislation_version[bill.legislation_version.length - 1];

			return {
				...bill,
				latestVersion,
			};
		}),
	search: publicProcedure
		.input(
			z.object({
				congress: z.optional(z.array(z.number())),
				chamber: z.optional(z.array(z.nativeEnum(legislationchamber))),
				versions: z.optional(z.array(z.string())),
				sort: z.optional(
					z.array(
						z.object({
							number: z.optional(z.enum(['asc', 'desc'])),
						}),
					),
				),
				query: z.optional(z.string()),
				page: z.number(),
				pageSize: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { query, congress, chamber, sort, page, pageSize } = input;

			console.log(input);

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

			const defaultSort = {
				number: SortOrder.desc,
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
					legislation_action: {
						select: {
							legislation_action_id: true,
						},
						where: {
							action_code: 'E40000',
						},
					},
					congress: {
						select: {
							session_number: true,
						},
					},
				},
				where,
				orderBy: sort ? sort : defaultSort,
				skip: (page - 1) * pageSize,
				take: pageSize,
			});

			return {
				legislation: legislation.map((legislation) => ({
					...legislation,
					signed: legislation.legislation_action[0],
				})),
				totalResults,
			};
		}),
	appropriations: publicProcedure
		.input(
			z.object({
				id: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const legislation = await ctx.db.legislation.findUniqueOrThrow({
				select: {
					legislation_version: {
						select: {
							legislation_version_id: true,
						},
					},
				},
				where: { legislation_id: input.id },
			});

			const latestVersion =
				legislation.legislation_version[
					legislation.legislation_version.length - 1
				];

			const appropriations = await ctx.db.appropriation.findMany({
				select: {
					appropriation_id: true,
					purpose: true,
					amount: true,
					until_expended: true,
					new_spending: true,
					fiscal_years: true,
				},
				where: {
					legislation_version_id:
						latestVersion?.legislation_version_id,
					amount: { not: 0 },
				},
			});

			return appropriations.map((appropriation) => ({
				...appropriation,
				id: appropriation.appropriation_id,
				amount: Number(appropriation.amount),
			}));
		}),
	diffs: publicProcedure
		.input(
			z.object({
				id: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const legislation = await ctx.db.legislation.findUniqueOrThrow({
				select: {
					legislation_version: {
						select: {
							version_id: true,
						},
					},
				},
				where: { legislation_id: input.id },
			});

			const latestVersion =
				legislation.legislation_version[
					legislation.legislation_version.length - 1
				];

			if (!latestVersion) {
				return { diffs: [], mergedTree: null };
			}

			const diffs = await ctx.db.usc_content_diff.findMany({
				select: {
					usc_content_id: true,
					usc_content_diff_id: true,
					section_display: true,
					heading: true,
					content_str: true,
					usc_chapter: {
						select: {
							short_title: true,
							long_title: true,
						},
					},
					usc_section: {
						select: {
							number: true,
							heading: true,
						},
					},
				},
				where: {
					version_id: latestVersion.version_id,
				},
				orderBy: [
					{ usc_chapter: { short_title: 'asc' } },
					{ usc_section: { number: 'asc' } },
					{ usc_content_id: 'asc' },
				],
			});

			const allDiffTrees = await buildNestedDiffTrees(ctx.db, diffs);
			const mergedTree = mergeDiffTrees(allDiffTrees);

			return {
				diffs: diffs.reduce(
					(acc, diff) => {
						acc[diff.usc_content_id] = diff;
						return acc;
					},
					{} as { [key: number]: (typeof diffs)[0] },
				),
				mergedTree,
			};
		}),
});
