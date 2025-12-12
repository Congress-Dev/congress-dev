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
							created_at: true,
							effective_date: true,
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
					version_id: latestVersion?.version_id,
					usc_section: {
						number: '1182',
					},
				},
				// skip: 3,
			});

			/**
			 * Fetches the full parent chain for a given USC Content ID.
			 * Returns array from root -> leaf (target item).
			 */
			async function fetchParentChain(uscContentId: number) {
				const chain = [];
				let current: number | null = uscContentId;

				while (current) {
					const node = await ctx.db.usc_content.findUnique({
						where: { usc_content_id: current },
						select: {
							usc_content_id: true,
							parent_id: true,
							content_str: true,
							heading: true,
							section_display: true,
						},
					});

					if (!node) break;

					chain.push(node);
					current = node.parent_id;
				}

				return chain.reverse();
			}

			/**
			 * Given a node, fetch all children (direct descendants).
			 */
			async function fetchChildren(parentId: number | null) {
				return ctx.db.usc_content.findMany({
					where: { parent_id: parentId },
					select: {
						parent_id: true,
						heading: true,
						content_str: true,
						usc_content_id: true,
						section_display: true,
					},
					orderBy: { usc_content_id: 'asc' },
				});
			}

			/**
			 * Slice siblings so only ±3 around the target remain.
			 */
			function sliceSiblingsAroundTarget(
				siblings: any[],
				targetId: number,
			) {
				const idx = siblings.findIndex(
					(s) => s.usc_content_id === targetId,
				);
				if (idx === -1) return siblings;

				const start = Math.max(idx - 3, 0);
				const end = Math.min(idx + 3, siblings.length - 1);

				return siblings.slice(start, end + 1);
			}

			/**
			 * Build a nested structure from the root to the target.
			 * Only include siblings within ±3 range at each level.
			 */
			async function buildNestedTree(chain: any[], targetId: number) {
				let cursor: TreeNode | null = null;
				let rootNode: TreeNode | null = null;

				for (let i = 0; i < chain.length; i++) {
					const node = chain[i];

					let visibleSiblings = [node];

					if (i === chain.length - 1) {
						// Fetch siblings at this parent level
						const siblings = await fetchChildren(node.parent_id);

						// Only keep ±3 siblings around the current chain node
						visibleSiblings = sliceSiblingsAroundTarget(
							siblings,
							node.usc_content_id,
						);
					}

					const children: TreeNode[] = visibleSiblings.map((sib) => ({
						id: sib.usc_content_id,
						usc_content_id: sib.usc_content_id,
						parent_id: sib.parent_id,
						content_str: sib.content_str,
						section_display: sib.section_display,
						heading: sib.heading,
						children: [],
						isTarget: sib.usc_content_id === targetId,
						isOnPath: sib.usc_content_id === node.usc_content_id,
						isCollapsed: sib.usc_content_id !== node.usc_content_id, // collapse siblings except the one on the path
					}));

					const thisNode = children.find(
						(c) => c.usc_content_id === node.usc_content_id,
					)!;

					if (!cursor) {
						// this is the root
						rootNode = thisNode;
						cursor = thisNode;
					} else {
						// attach to previous cursor
						cursor.children = children;
						cursor = thisNode;
					}
				}

				return rootNode!;
			}

			/**
			 * Main function: builds a nested "GitHub-like collapsed tree" for each diff.
			 */
			async function buildNestedDiffTrees() {
				const results = [];

				for (const diff of diffs) {
					const chain = await fetchParentChain(diff.usc_content_id);
					const tree = await buildNestedTree(
						chain,
						diff.usc_content_id,
					);

					results.push({
						diff: {
							usc_content_diff_id: diff.usc_content_diff_id,
							section_display: diff.section_display,
							heading: diff.heading,
							content_str: diff.content_str,
						},
						diffId: diff.usc_content_id,
						diffStr: diff.content_str,
						usc_chapter: diff.usc_chapter,
						usc_section: diff.usc_section,
						usc_content_id: diff.usc_content_id,
						tree,
					});
				}

				return results;
			}

			const data = await buildNestedDiffTrees();
			// const data = await buildMergedDiffTree();
			return data;
		}),
});
