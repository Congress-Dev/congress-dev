import { z } from 'zod';
import { createTRPCRouter, publicProcedure } from '~/server/api/trpc';

export const uscodeRouter = createTRPCRouter({
	releases: publicProcedure.query(async ({ ctx }) => {
		const releases = await ctx.db.usc_release.findMany({
			select: {
				usc_release_id: true,
				short_title: true,
				effective_date: true,
				long_title: true,
			},
			orderBy: { effective_date: 'desc' },
		});
		return releases;
	}),

	titles: publicProcedure
		.input(z.object({ releaseId: z.number() }))
		.query(async ({ input, ctx }) => {
			const titles = await ctx.db.usc_chapter.findMany({
				where: { usc_release_id: input.releaseId },
				select: {
					usc_chapter_id: true,
					short_title: true,
					long_title: true,
					usc_release_id: true,
				},
				orderBy: { usc_chapter_id: 'asc' },
			});
			return titles;
		}),

	levels: publicProcedure
		.input(
			z.object({
				chapterId: z.number(),
				parentId: z.number().nullable(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const sections = await ctx.db.usc_section.findMany({
				where: {
					usc_chapter_id: input.chapterId,
					parent_id: input.parentId,
				},
				select: {
					usc_section_id: true,
					usc_ident: true,
					number: true,
					section_display: true,
					heading: true,
					content_type: true,
					usc_chapter_id: true,
					parent_id: true,
				},
				orderBy: { usc_section_id: 'asc' },
			});
			return sections;
		}),

	lineage: publicProcedure
		.input(
			z.object({
				chapterId: z.number(),
				sectionNumber: z.string(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const section = await ctx.db.usc_section.findFirst({
				where: {
					usc_chapter_id: input.chapterId,
					number: input.sectionNumber,
				},
			});

			if (!section) return [];

			const lineage = [section];
			let current = section;
			let maxDepth = 20;

			while (current.parent_id && maxDepth > 0) {
				maxDepth--;
				const parent = await ctx.db.usc_section.findFirst({
					where: {
						usc_section_id: current.parent_id,
						usc_chapter_id: input.chapterId,
					},
				});
				if (!parent) break;
				lineage.push(parent);
				current = parent;
				if (!current.parent_id) break;
			}

			return lineage.map((s) => ({
				usc_section_id: s.usc_section_id,
				usc_ident: s.usc_ident,
				number: s.number,
				section_display: s.section_display,
				heading: s.heading,
				content_type: s.content_type,
				usc_chapter_id: s.usc_chapter_id,
				parent_id: s.parent_id,
			}));
		}),

	sectionContent: publicProcedure
		.input(
			z.object({
				chapterId: z.number(),
				sectionNumber: z.string(),
			}),
		)
		.query(async ({ input, ctx }) => {
			const section = await ctx.db.usc_section.findFirst({
				where: {
					usc_chapter_id: input.chapterId,
					number: input.sectionNumber,
					content_type: 'section',
				},
			});

			if (!section) return null;

			const content = await ctx.db.usc_content.findMany({
				where: { usc_section_id: section.usc_section_id },
				select: {
					usc_content_id: true,
					usc_ident: true,
					parent_id: true,
					order_number: true,
					section_display: true,
					heading: true,
					content_str: true,
					content_type: true,
					number: true,
					usc_section_id: true,
				},
				orderBy: { usc_content_id: 'asc' },
			});

			return content;
		}),
});
