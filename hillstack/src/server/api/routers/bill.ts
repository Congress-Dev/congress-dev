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
					usc_content_diff_id: true,
					content_str: true,
					usc_chapter: {
						select: {
							short_title: true,
							long_title: true,
							usc_chapter_id: true,
						},
					},
					usc_section: {
						select: {
							number: true,
							heading: true,
							section_display: true,
							usc_section_id: true,
						},
					},
					usc_content: {
						select: {
							parent_id: true,
							usc_ident: true,
							usc_content_id: true,
							content_str: true,
							version_id: true,
						},
					},
				},
				where: {
					version_id: latestVersion?.version_id,
				},
				orderBy: {},
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

				for (let i = 1; i < chain.length; i++) {
					const node = chain[i];

					// Fetch siblings at this parent level
					const siblings = await fetchChildren(node.parent_id);

					// Only keep ±3 siblings around the current chain node
					const visibleSiblings = sliceSiblingsAroundTarget(
						siblings,
						node.usc_content_id,
					);

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
				const diffs = await ctx.db.usc_content_diff.findMany({
					select: {
						usc_content_id: true,
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
					},
				});

				const results = [];

				for (const diff of diffs) {
					const chain = await fetchParentChain(diff.usc_content_id);
					const tree = await buildNestedTree(
						chain,
						diff.usc_content_id,
					);

					results.push({
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
			return data;
			// I want to do the following.
			// - Group each diff by its parent usc chapter
			// - For each diff, I want to pull the tree structure up to the parent (start of chapter)
			// - I want to create a tree structure where each diff is placed in the correct level
			// - For the last level of parents, (i.e right above the diff level), I want to pull all surrounding content

			// const chapters = Array.from(
			// 	new Set(diffs.map((diff) => diff.usc_chapter?.usc_chapter_id)),
			// );
			// const tree = {};

			// await Promise.all(
			// 	diffs.map(async (diff) => {
			// 		const { usc_chapter, usc_section, usc_content } = diff;
			// 		const chapterId = usc_chapter?.usc_chapter_id;
			// 		const sectionId = usc_section?.usc_section_id;

			// 		console.log(usc_chapter?.long_title);
			// 		console.log(usc_section?.heading);
			// 		console.log('___');

			// 		tree[chapterId] ??= { usc_chapter, children: {} };
			// 		tree[chapterId].children[sectionId] ??= {
			// 			usc_section,
			// 			children: {},
			// 		};

			// 		const result = await ctx.db.$queryRawUnsafe(
			// 			`
			// 		WITH RECURSIVE cte AS (
			// 			SELECT *
			// 			FROM "usc_content"
			// 			WHERE usc_content_id = $1 AND version_id=1
			// 			UNION ALL
			// 			SELECT c.*
			// 			FROM "usc_content" c
			// 			JOIN cte ON cte."parent_id" = c.usc_content_id
			// 		)
			// 		SELECT * FROM cte;
			// 		`,
			// 			usc_content?.parent_id,
			// 		);

			// 		result.reverse();
			// 		result.push(diff);
			// 		result.splice(0, 1);

			// 		const firstHeader = result[0];

			// 		tree[chapterId].children[sectionId].children[
			// 			firstHeader.usc_content_id
			// 		] = result;
			// 	}),
			// );

			// return tree;

			// const diffParentMap = diffs.reduce((acc, diff) => {
			// 	acc[diff.usc_content?.parent_id] ??= [];
			// 	acc[diff.usc_content?.parent_id].push(diff);
			// 	return acc;
			// }, {}); // = diffs.map((diff) => diff.usc_content?.parent_id);

			// console.log(Object.keys(diffParentMap));

			// const surrounding = await ctx.db.usc_content.findMany({
			// 	select: {
			// 		parent_id: true,
			// 		usc_content_id: true,
			// 		content_str: true,
			// 		heading: true,
			// 		usc_ident: true,
			// 	},
			// 	where: {
			// 		parent_id: {
			// 			in: Object.keys(diffParentMap).map((key) =>
			// 				Number(key),
			// 			),
			// 		},
			// 		version_id: 1,
			// 	},
			// });

			// const parents = await ctx.db.usc_content.findMany({
			// 	select: {
			// 		parent_id: true,
			// 		usc_content_id: true,
			// 		content_str: true,
			// 		heading: true,
			// 		usc_ident: true,
			// 	},
			// 	where: {
			// 		usc_content_id: {
			// 			in: Object.keys(diffParentMap).map((key) =>
			// 				Number(key),
			// 			),
			// 		},
			// 		version_id: 1,
			// 	},
			// });

			// const parentMap = parents.reduce((acc, parent) => {
			// 	acc[parent.usc_content_id] = parent;
			// 	return acc;
			// }, {});

			// const extras = surrounding.reduce((acc, content) => {
			// 	acc[content.parent_id] ??= {
			// 		diff: diffParentMap[content.parent_id],
			// 		sections: [],
			// 		parent: parentMap[content.parent_id],
			// 	};
			// 	acc[content.parent_id].sections.push(content);
			// 	return acc;
			// }, {});

			// const result = await ctx.db.$queryRawUnsafe(
			// 	`
			// 	WITH RECURSIVE cte AS (
			// 		SELECT *
			// 		FROM "usc_content"
			// 		WHERE usc_content_id = $1
			// 		UNION ALL
			// 		SELECT c.*
			// 		FROM "usc_content" c
			// 		JOIN cte ON cte."parent_id" = c.usc_content_id
			// 	)
			// 	SELECT * FROM cte;
			// 	`,
			// 	diffs[0]?.usc_content?.parent_id,
			// );

			// // const surrounding = await ctx.db.usc_content.findMany({
			// // 	select: {
			// // 		content_str: true,
			// // 	},
			// // 	where: {
			// // 		usc_content_id: {
			// // 			in: [
			// // 				diffs[0]?.usc_content?.usc_content_id - 1,
			// // 				diffs[0]?.usc_content?.usc_content_id + 1,
			// // 			],
			// // 		},
			// // 	},
			// // });

			// return {
			// 	version_id: latestVersion?.version_id,
			// 	diffs,
			// 	extras,
			// 	result,
			// };
		}),
});
