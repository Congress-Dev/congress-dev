import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const congressionalRecordRouter = createTRPCRouter({
	list: publicProcedure
		.input(
			z.object({
				page: z.number().default(1),
				pageSize: z.number().default(20),
				startDate: z.string().optional(),
				endDate: z.string().optional(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { page, pageSize, startDate, endDate } = input;

			const where: Record<string, unknown> = {};
			if (startDate || endDate) {
				where.issue_date = {};
				if (startDate) (where.issue_date as Record<string, unknown>).gte = new Date(startDate);
				if (endDate) (where.issue_date as Record<string, unknown>).lte = new Date(endDate);
			}

			const [issues, totalResults] = await Promise.all([
				ctx.db.crec_issue.findMany({
					select: {
						crec_issue_id: true,
						issue_date: true,
						congress_id: true,
						package_id: true,
						crec_granule: {
							select: {
								crec_granule_id: true,
								section: true,
							},
						},
					},
					where,
					orderBy: { issue_date: 'desc' },
					skip: (page - 1) * pageSize,
					take: pageSize,
				}),
				ctx.db.crec_issue.count({ where }),
			]);

			return { issues, totalResults };
		}),

	getIssue: publicProcedure
		.input(z.object({ issueId: z.number() }))
		.query(async ({ input, ctx }) => {
			const issue = await ctx.db.crec_issue.findUniqueOrThrow({
				select: {
					crec_issue_id: true,
					issue_date: true,
					congress_id: true,
					package_id: true,
					crec_granule: {
						select: {
							crec_granule_id: true,
							granule_id: true,
							section: true,
							title: true,
							page_start: true,
							page_end: true,
							order_number: true,
							crec_summary: {
								select: {
									summary: true,
								},
								where: {
									summary_type: 'granule',
								},
								take: 1,
							},
							_count: {
								select: {
									crec_speech: true,
								},
							},
						},
						orderBy: { order_number: 'asc' },
					},
					crec_summary: {
						select: {
							summary: true,
							summary_type: true,
						},
						where: {
							summary_type: 'daily',
						},
					},
				},
				where: { crec_issue_id: input.issueId },
			});

			return issue;
		}),

	getGranule: publicProcedure
		.input(z.object({ granuleId: z.number() }))
		.query(async ({ input, ctx }) => {
			const granule = await ctx.db.crec_granule.findUniqueOrThrow({
				select: {
					crec_granule_id: true,
					crec_issue_id: true,
					granule_id: true,
					section: true,
					title: true,
					page_start: true,
					page_end: true,
					crec_speech: {
						select: {
							crec_speech_id: true,
							speaker_raw: true,
							legislator_bioguide_id: true,
							order_number: true,
							content_text: true,
							word_count: true,
							legislator: {
								select: {
									first_name: true,
									last_name: true,
									party: true,
									state: true,
									image_url: true,
								},
							},
							crec_bill_reference: {
								select: {
									crec_bill_reference_id: true,
									legislation_id: true,
									cite_text: true,
									cite_type: true,
									start_offset: true,
									end_offset: true,
									legislation: {
										select: {
											legislation_id: true,
											title: true,
											number: true,
											chamber: true,
										},
									},
								},
							},
						},
						orderBy: { order_number: 'asc' },
					},
					crec_summary: {
						select: {
							summary: true,
						},
						where: {
							summary_type: 'granule',
						},
						take: 1,
					},
				},
				where: { crec_granule_id: input.granuleId },
			});

			return granule;
		}),

	speakerStats: publicProcedure
		.input(
			z.object({
				startDate: z.string().optional(),
				endDate: z.string().optional(),
				chamber: z.string().optional(),
				limit: z.number().default(20),
				page: z.number().default(1),
			}),
		)
		.query(async ({ input, ctx }) => {
			const { startDate, endDate, chamber, limit, page } = input;

			// Build date filter for the join through granule -> issue
			const granuleWhere: Record<string, unknown> = {};
			if (chamber) {
				granuleWhere.section = chamber;
			}
			if (startDate || endDate) {
				const dateFilter: Record<string, unknown> = {};
				if (startDate) dateFilter.gte = new Date(startDate);
				if (endDate) dateFilter.lte = new Date(endDate);
				granuleWhere.crec_issue = { issue_date: dateFilter };
			}

			// Use raw SQL for aggregation since Prisma doesn't support groupBy with sum well
			const dateConditions: string[] = [];
			const params: unknown[] = [];
			let paramIdx = 1;

			if (startDate) {
				dateConditions.push(`ci.issue_date >= $${paramIdx}::date`);
				params.push(startDate);
				paramIdx++;
			}
			if (endDate) {
				dateConditions.push(`ci.issue_date <= $${paramIdx}::date`);
				params.push(endDate);
				paramIdx++;
			}
			if (chamber) {
				dateConditions.push(`cg.section = $${paramIdx}::text`);
				params.push(chamber);
				paramIdx++;
			}

			const whereClause = dateConditions.length > 0
				? `AND ${dateConditions.join(' AND ')}`
				: '';

			const offset = (page - 1) * limit;
			params.push(limit, offset);

			const results = await ctx.db.$queryRawUnsafe<Array<{
				bioguide_id: string;
				first_name: string | null;
				last_name: string | null;
				party: string | null;
				state: string | null;
				image_url: string | null;
				total_words: bigint;
				speech_count: bigint;
			}>>(
				`SELECT
					cs.legislator_bioguide_id as bioguide_id,
					l.first_name,
					l.last_name,
					l.party,
					l.state,
					l.image_url,
					SUM(cs.word_count)::bigint as total_words,
					COUNT(cs.crec_speech_id)::bigint as speech_count
				FROM crec_speech cs
				JOIN crec_granule cg ON cs.crec_granule_id = cg.crec_granule_id
				JOIN crec_issue ci ON cg.crec_issue_id = ci.crec_issue_id
				JOIN legislator l ON cs.legislator_bioguide_id = l.bioguide_id
				WHERE cs.legislator_bioguide_id IS NOT NULL ${whereClause}
				GROUP BY cs.legislator_bioguide_id, l.first_name, l.last_name, l.party, l.state, l.image_url
				ORDER BY total_words DESC
				LIMIT $${paramIdx} OFFSET $${paramIdx + 1}`,
				...params,
			);

			const countResult = await ctx.db.$queryRawUnsafe<Array<{ count: bigint }>>(
				`SELECT COUNT(DISTINCT cs.legislator_bioguide_id)::bigint as count
				FROM crec_speech cs
				JOIN crec_granule cg ON cs.crec_granule_id = cg.crec_granule_id
				JOIN crec_issue ci ON cg.crec_issue_id = ci.crec_issue_id
				WHERE cs.legislator_bioguide_id IS NOT NULL ${whereClause}`,
				...params.slice(0, params.length - 2),
			);

			return {
				speakers: results.map((r) => ({
					...r,
					total_words: Number(r.total_words),
					speech_count: Number(r.speech_count),
				})),
				totalResults: Number(countResult[0]?.count ?? 0),
			};
		}),

	activityCalendar: publicProcedure
		.input(
			z.object({
				startDate: z.string().optional(),
				endDate: z.string().optional(),
			}).optional(),
		)
		.query(async ({ input, ctx }) => {
			const where: Record<string, unknown> = {};
			if (input?.startDate || input?.endDate) {
				where.issue_date = {};
				if (input?.startDate) (where.issue_date as Record<string, unknown>).gte = new Date(input.startDate);
				if (input?.endDate) (where.issue_date as Record<string, unknown>).lte = new Date(input.endDate);
			}

			const issues = await ctx.db.crec_issue.findMany({
				select: {
					issue_date: true,
					_count: {
						select: {
							crec_granule: true,
						},
					},
				},
				where,
				orderBy: { issue_date: 'asc' },
			});

			return issues.map((i) => ({
				date: i.issue_date,
				count: i._count.crec_granule,
			}));
		}),

	// For bill detail page - get debates referencing a specific bill
	debatesForBill: publicProcedure
		.input(z.object({ legislationId: z.number() }))
		.query(async ({ input, ctx }) => {
			const references = await ctx.db.crec_bill_reference.findMany({
				select: {
					cite_text: true,
					crec_speech: {
						select: {
							crec_speech_id: true,
							speaker_raw: true,
							legislator_bioguide_id: true,
							content_text: true,
							word_count: true,
							legislator: {
								select: {
									first_name: true,
									last_name: true,
									party: true,
								},
							},
							crec_granule: {
								select: {
									crec_granule_id: true,
									crec_issue_id: true,
									title: true,
									section: true,
									crec_issue: {
										select: {
											issue_date: true,
										},
									},
								},
							},
						},
					},
				},
				where: {
					legislation_id: input.legislationId,
				},
				take: 50,
			});

			return references;
		}),

	// For legislator page - get speaking stats for a specific legislator
	legislatorStats: publicProcedure
		.input(z.object({ bioguideId: z.string() }))
		.query(async ({ input, ctx }) => {
			const stats = await ctx.db.$queryRawUnsafe<Array<{
				total_words: bigint;
				speech_count: bigint;
				first_date: Date | null;
				last_date: Date | null;
			}>>(
				`SELECT
					SUM(cs.word_count)::bigint as total_words,
					COUNT(cs.crec_speech_id)::bigint as speech_count,
					MIN(ci.issue_date) as first_date,
					MAX(ci.issue_date) as last_date
				FROM crec_speech cs
				JOIN crec_granule cg ON cs.crec_granule_id = cg.crec_granule_id
				JOIN crec_issue ci ON cg.crec_issue_id = ci.crec_issue_id
				WHERE cs.legislator_bioguide_id = $1`,
				input.bioguideId,
			);

			const recentSpeeches = await ctx.db.crec_speech.findMany({
				select: {
					crec_speech_id: true,
					content_text: true,
					word_count: true,
					crec_granule: {
						select: {
							crec_granule_id: true,
							crec_issue_id: true,
							title: true,
							section: true,
							crec_issue: {
								select: {
									issue_date: true,
								},
							},
						},
					},
				},
				where: {
					legislator_bioguide_id: input.bioguideId,
				},
				orderBy: {
					crec_speech_id: 'desc',
				},
				take: 10,
			});

			const stat = stats[0];
			return {
				totalWords: Number(stat?.total_words ?? 0),
				speechCount: Number(stat?.speech_count ?? 0),
				firstDate: stat?.first_date ?? null,
				lastDate: stat?.last_date ?? null,
				recentSpeeches,
			};
		}),
});
