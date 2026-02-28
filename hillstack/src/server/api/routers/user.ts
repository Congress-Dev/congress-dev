import { z } from 'zod';
import { createTRPCRouter, privateProcedure } from '~/server/api/trpc';

const FASTAPI_URL = process.env.FASTAPI_URL ?? 'http://localhost:8080';

export const userRouter = createTRPCRouter({
	legislationFollowing: privateProcedure
		.input(
			z.object({
				legislation_id: z.number(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const existingFollow = await ctx.db.user_legislation.findFirst({
				select: {
					user_legislation_id: true,
				},
				where: {
					legislation_id: input.legislation_id,
					user_id: ctx.session?.user?.email,
				},
			});

			return Boolean(existingFollow);
		}),
	legislationFollow: privateProcedure
		.input(
			z.object({
				legislation_id: z.number(),
			}),
		)
		.mutation(async ({ input, ctx }) => {
			const existingFollow = await ctx.db.user_legislation.findFirst({
				select: {
					user_legislation_id: true,
				},
				where: {
					legislation_id: input.legislation_id,
					user_id: ctx.user.email,
				},
			});

			if (existingFollow) {
				await ctx.db.user_legislation.delete({
					where: {
						user_legislation_id: existingFollow.user_legislation_id,
					},
				});
			} else {
				await ctx.db.user_legislation.create({
					data: {
						legislation_id: input.legislation_id,
						user_id: ctx.user.email,
					},
				});
			}
		}),
	legislatorFollowing: privateProcedure
		.input(
			z.object({
				bioguide_id: z.string(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const existingFollow = await ctx.db.user_legislator.findFirst({
				select: {
					user_legislator_id: true,
				},
				where: {
					bioguide_id: input.bioguide_id,
					user_id: ctx.user.email,
				},
			});

			return Boolean(existingFollow);
		}),
	legislatorFollow: privateProcedure
		.input(
			z.object({
				bioguide_id: z.string(),
			}),
		)
		.mutation(async ({ input, ctx }) => {
			const existingFollow = await ctx.db.user_legislator.findFirst({
				select: {
					user_legislator_id: true,
				},
				where: {
					bioguide_id: input.bioguide_id,
					user_id: ctx.user.email,
				},
			});

			if (existingFollow) {
				await ctx.db.user_legislator.delete({
					where: {
						user_legislator_id: existingFollow.user_legislator_id,
					},
				});
			} else {
				await ctx.db.user_legislator.create({
					data: {
						bioguide_id: input.bioguide_id,
						user_id: ctx.user.email,
					},
				});
			}
		}),
	legislationFeed: privateProcedure.query(async ({ ctx }) => {
		const userLegislation = await ctx.db.user_legislation.findMany({
			select: {
				legislation: {
					select: {
						title: true,
						number: true,
						legislation_id: true,
						congress: {
							select: {
								session_number: true,
							},
						},
						chamber: true,
						legislation_sponsorship: {
							select: {
								legislator: {
									select: {
										first_name: true,
										last_name: true,
									},
								},
							},
							where: {
								cosponsor: false,
							},
						},
					},
				},
			},
			where: {
				user_id: ctx.user.email,
			},
			take: 10,
		});

		return userLegislation.map((leg) => leg.legislation);
	}),
	legislatorFeed: privateProcedure.query(async ({ ctx }) => {
		const oneWeekAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

		const userLegislators = await ctx.db.user_legislator.findMany({
			select: {
				bioguide_id: true,
			},
			where: {
				user_id: ctx.user.email,
			},
		});

		if (userLegislators.length === 0) {
			return [];
		}

		const userLegislation = await ctx.db.legislation.findMany({
			select: {
				title: true,
				number: true,
				legislation_id: true,
				congress: {
					select: {
						session_number: true,
					},
				},
				chamber: true,
				legislation_sponsorship: {
					select: {
						legislator: {
							select: {
								first_name: true,
								last_name: true,
							},
						},
					},
					where: {
						cosponsor: false,
					},
				},
			},
			take: 10,
			where: {
				legislation_sponsorship: {
					some: {
						legislator: {
							bioguide_id: {
								in: userLegislators.flatMap(
									(leg) => leg.bioguide_id as string,
								),
							},
						},
					},
				},
				legislation_version: {
					some: {
						effective_date: {
							gte: oneWeekAgo,
						},
					},
				},
			},
		});

		return userLegislation.map((leg) => leg);
	}),

	// ── Interest procedures ──────────────────────────────────────────────────

	interestGet: privateProcedure.query(async ({ ctx }) => {
		const interest = await ctx.db.user_interest.findFirst({
			where: { user_id: ctx.user.email },
			include: {
				user_interest_usc_content: {
					orderBy: { match_rank: 'asc' },
				},
			},
		});

		if (
			!interest ||
			interest.user_interest_usc_content.length === 0
		) {
			return interest
				? { ...interest, sectionHeadings: {} as Record<string, string> }
				: null;
		}

		const idents = interest.user_interest_usc_content
			.map((m) => m.usc_ident)
			.filter((id): id is string => Boolean(id));

		if (idents.length === 0) {
			return { ...interest, sectionHeadings: {} as Record<string, string> };
		}

		// Look up section headings from usc_section
		const sectionRows = await ctx.db.usc_section.findMany({
			where: { usc_ident: { in: idents } },
			select: { usc_ident: true, heading: true, section_display: true },
			distinct: ['usc_ident'],
			orderBy: { version_id: 'desc' },
		});

		const sectionHeadings: Record<string, string> = {};
		for (const row of sectionRows) {
			if (row.usc_ident && row.heading) {
				sectionHeadings[row.usc_ident] = row.heading;
			}
		}

		// For idents not found in usc_section, try usc_content
		const missingIdents = idents.filter((id) => !sectionHeadings[id]);
		if (missingIdents.length > 0) {
			const contentRows = await ctx.db.usc_content.findMany({
				where: {
					usc_ident: { in: missingIdents },
					heading: { not: null },
				},
				select: { usc_ident: true, heading: true, section_display: true },
				distinct: ['usc_ident'],
				orderBy: { version_id: 'desc' },
			});
			for (const row of contentRows) {
				if (row.usc_ident && row.heading) {
					sectionHeadings[row.usc_ident] = row.heading;
				}
			}
		}

		return { ...interest, sectionHeadings };
	}),

	interestSave: privateProcedure
		.input(z.object({ interest_text: z.string().min(1).max(500) }))
		.mutation(async ({ input, ctx }) => {
			// 1. Upsert the interest record
			const existing = await ctx.db.user_interest.findFirst({
				where: { user_id: ctx.user.email },
			});

			let interestId: number;
			if (existing) {
				await ctx.db.user_interest.update({
					where: { user_interest_id: existing.user_interest_id },
					data: {
						interest_text: input.interest_text,
						updated_at: new Date(),
					},
				});
				interestId = existing.user_interest_id;
			} else {
				const created = await ctx.db.user_interest.create({
					data: {
						user_id: ctx.user.email,
						interest_text: input.interest_text,
					},
				});
				interestId = created.user_interest_id;
			}

			// 2. Call the FastAPI ChromaDB search endpoint (no auth needed)
			let chromaMatches: Array<{
				usc_ident?: string;
				title?: string;
				section_display?: string;
				usc_link?: string;
			}> = [];
			try {
				const res = await fetch(`${FASTAPI_URL}/uscode/search`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						query: input.interest_text,
						results: 20,
					}),
				});
				if (res.ok) {
					chromaMatches = await res.json();
				} else{
          console.error('ChromaDB search failed:', await res.text());
        }
			} catch {
				// ChromaDB unavailable — interest saved, matches will be empty
			}

			// 3. Deactivate old auto-matched sections
			await ctx.db.user_interest_usc_content.updateMany({
				where: {
					user_interest_id: interestId,
					match_source: 'auto',
				},
				data: { is_active: false },
			});

			// 4. Upsert new auto-matched sections
			for (let rank = 0; rank < chromaMatches.length; rank++) {
				const match = chromaMatches[rank];
				const usc_ident = match?.usc_ident;
				if (!usc_ident) continue;

				const existingMatch =
					await ctx.db.user_interest_usc_content.findFirst({
						where: { user_interest_id: interestId, usc_ident },
					});

				if (existingMatch) {
					await ctx.db.user_interest_usc_content.update({
						where: {
							user_interest_usc_content_id:
								existingMatch.user_interest_usc_content_id,
						},
						data: {
							is_active: true,
							match_rank: rank,
							match_source: 'auto',
						},
					});
				} else {
					await ctx.db.user_interest_usc_content.create({
						data: {
							user_interest_id: interestId,
							usc_ident,
							match_source: 'auto',
							is_active: true,
							match_rank: rank,
						},
					});
				}
			}

			return ctx.db.user_interest.findFirst({
				where: { user_id: ctx.user.email },
				include: {
					user_interest_usc_content: {
						orderBy: { match_rank: 'asc' },
					},
				},
			});
		}),

	interestToggleSection: privateProcedure
		.input(
			z.object({
				user_interest_usc_content_id: z.number(),
				is_active: z.boolean(),
			}),
		)
		.mutation(async ({ input, ctx }) => {
			// Verify ownership before updating
			const interest = await ctx.db.user_interest.findFirst({
				where: { user_id: ctx.user.email },
			});
			if (!interest) return;

			await ctx.db.user_interest_usc_content.updateMany({
				where: {
					user_interest_usc_content_id:
						input.user_interest_usc_content_id,
					user_interest_id: interest.user_interest_id,
				},
				data: { is_active: input.is_active },
			});
		}),

	interestAddSection: privateProcedure
		.input(z.object({ usc_ident: z.string() }))
		.mutation(async ({ input, ctx }) => {
			const interest = await ctx.db.user_interest.findFirst({
				where: { user_id: ctx.user.email },
			});
			if (!interest) return;

			const existing =
				await ctx.db.user_interest_usc_content.findFirst({
					where: {
						user_interest_id: interest.user_interest_id,
						usc_ident: input.usc_ident,
					},
				});

			if (existing) {
				await ctx.db.user_interest_usc_content.update({
					where: {
						user_interest_usc_content_id:
							existing.user_interest_usc_content_id,
					},
					data: { is_active: true, match_source: 'manual' },
				});
			} else {
				await ctx.db.user_interest_usc_content.create({
					data: {
						user_interest_id: interest.user_interest_id,
						usc_ident: input.usc_ident,
						match_source: 'manual',
						is_active: true,
					},
				});
			}
		}),

	interestLegislation: privateProcedure.query(async ({ ctx }) => {
		const interest = await ctx.db.user_interest.findFirst({
			where: { user_id: ctx.user.email },
			include: {
				user_interest_usc_content: {
					where: { is_active: true },
					select: { usc_ident: true },
				},
			},
		});

		if (
			!interest ||
			interest.user_interest_usc_content.length === 0
		) {
			return [];
		}

		const idents = interest.user_interest_usc_content
			.map((m) => m.usc_ident)
			.filter((id): id is string => Boolean(id));

		if (idents.length === 0) return [];

		// Build a raw SQL query since Prisma doesn't support ILIKE prefix arrays
		const identsWithWildcard = idents.map((id) => `${id}%`);
		const orClauses = identsWithWildcard
			.map((_, i) => `uc.usc_ident ILIKE $${i + 1}`)
			.join(' OR ');

		// Collect matched ident per bill using array_agg
		type LegislationRow = {
			legislation_id: bigint;
			title: string;
			number: number;
			session_number: number;
			legislation_type: string;
			chamber: string;
			effective_date: Date | null;
			matched_idents: string[];
		};

		const rows = await ctx.db.$queryRawUnsafe<LegislationRow[]>(
			`SELECT
				l.legislation_id,
				l.title,
				l.number,
				c.session_number,
				l.legislation_type,
				l.chamber,
				MIN(lv.effective_date) AS effective_date,
				ARRAY_AGG(DISTINCT uc.usc_ident) AS matched_idents
			FROM usc_content uc
			JOIN usc_content_diff ucd ON ucd.usc_content_id = uc.usc_content_id
			JOIN legislation_version lv ON lv.version_id = ucd.version_id
			JOIN legislation l ON l.legislation_id = lv.legislation_id
			JOIN congress c ON c.congress_id = l.congress_id
			WHERE ${orClauses}
			GROUP BY l.legislation_id, l.title, l.number, l.legislation_type, l.chamber, c.session_number
			ORDER BY MIN(lv.effective_date) DESC
			LIMIT 50`,
			...identsWithWildcard,
		);

		// Gather all matched idents to look up headings in bulk
		const allMatchedIdents = [
			...new Set(rows.flatMap((r) => r.matched_idents ?? [])),
		];

		const headingsMap: Record<string, string> = {};
		if (allMatchedIdents.length > 0) {
			const sectionRows = await ctx.db.usc_section.findMany({
				where: { usc_ident: { in: allMatchedIdents } },
				select: { usc_ident: true, heading: true },
				distinct: ['usc_ident'],
				orderBy: { version_id: 'desc' },
			});
			for (const row of sectionRows) {
				if (row.usc_ident && row.heading) {
					headingsMap[row.usc_ident] = row.heading;
				}
			}

			const missingIdents = allMatchedIdents.filter(
				(id) => !headingsMap[id],
			);
			if (missingIdents.length > 0) {
				const contentRows = await ctx.db.usc_content.findMany({
					where: {
						usc_ident: { in: missingIdents },
						heading: { not: null },
					},
					select: { usc_ident: true, heading: true },
					distinct: ['usc_ident'],
					orderBy: { version_id: 'desc' },
				});
				for (const row of contentRows) {
					if (row.usc_ident && row.heading) {
						headingsMap[row.usc_ident] = row.heading;
					}
				}
			}
		}

		// BigInt → number for JSON serialisation
		return rows.map((r) => ({
			...r,
			legislation_id: Number(r.legislation_id),
			matched_idents: r.matched_idents ?? [],
			matched_headings: Object.fromEntries(
				(r.matched_idents ?? [])
					.filter((id) => headingsMap[id])
					.map((id) => [id, headingsMap[id]]),
			),
		}));
	}),

	interestBillMatch: privateProcedure
		.input(z.object({ legislation_id: z.number() }))
		.query(async ({ input, ctx }) => {
			const interest = await ctx.db.user_interest.findFirst({
				where: { user_id: ctx.user.email },
				include: {
					user_interest_usc_content: {
						where: { is_active: true },
						select: { usc_ident: true },
					},
				},
			});

			const emptyResult = {
				matches: false,
				matchedIdents: [] as string[],
				matchedHeadings: {} as Record<string, string>,
				interestText: interest?.interest_text ?? '',
			};

			if (
				!interest ||
				interest.user_interest_usc_content.length === 0
			) {
				return emptyResult;
			}

			const idents = interest.user_interest_usc_content
				.map((m) => m.usc_ident)
				.filter((id): id is string => Boolean(id));

			if (idents.length === 0) {
				return emptyResult;
			}

			const identsWithWildcard = idents.map((id) => `${id}%`);
			const orClauses = identsWithWildcard
				.map((_, i) => `uc.usc_ident ILIKE $${i + 2}`)
				.join(' OR ');

			type IdentRow = { usc_ident: string };
			const rows = await ctx.db.$queryRawUnsafe<IdentRow[]>(
				`SELECT DISTINCT uc.usc_ident
				FROM usc_content uc
				JOIN usc_content_diff ucd ON ucd.usc_content_id = uc.usc_content_id
				JOIN legislation_version lv ON lv.version_id = ucd.version_id
				WHERE lv.legislation_id = $1
				AND (${orClauses})
				LIMIT 10`,
				input.legislation_id,
				...identsWithWildcard,
			);

			const matchedIdents = rows.map((r) => r.usc_ident);

			// Look up section headings for the matched idents
			const matchedHeadings: Record<string, string> = {};
			if (matchedIdents.length > 0) {
				const sectionRows = await ctx.db.usc_section.findMany({
					where: { usc_ident: { in: matchedIdents } },
					select: { usc_ident: true, heading: true },
					distinct: ['usc_ident'],
					orderBy: { version_id: 'desc' },
				});
				for (const row of sectionRows) {
					if (row.usc_ident && row.heading) {
						matchedHeadings[row.usc_ident] = row.heading;
					}
				}

				// Fall back to usc_content for any missing
				const missingIdents = matchedIdents.filter(
					(id) => !matchedHeadings[id],
				);
				if (missingIdents.length > 0) {
					const contentRows = await ctx.db.usc_content.findMany({
						where: {
							usc_ident: { in: missingIdents },
							heading: { not: null },
						},
						select: { usc_ident: true, heading: true },
						distinct: ['usc_ident'],
						orderBy: { version_id: 'desc' },
					});
					for (const row of contentRows) {
						if (row.usc_ident && row.heading) {
							matchedHeadings[row.usc_ident] = row.heading;
						}
					}
				}
			}

			return {
				matches: rows.length > 0,
				matchedIdents,
				matchedHeadings,
				interestText: interest.interest_text ?? '',
			};
		}),
});
