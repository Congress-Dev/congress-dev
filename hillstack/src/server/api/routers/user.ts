import { z } from 'zod';
import { createTRPCRouter, privateProcedure } from '~/server/api/trpc';

export const userRouter = createTRPCRouter({
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
					user_id: ctx.session.user.email,
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
			if (!ctx.session) {
				throw Error('Unauthorized');
			}

			const existingFollow = await ctx.db.user_legislator.findFirst({
				select: {
					user_legislator_id: true,
				},
				where: {
					bioguide_id: input.bioguide_id,
					user_id: ctx.session.user.email,
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
						user_id: ctx.session.user.email,
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
				user_id: ctx.session.user.email,
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
				user_id: ctx.session.user.email,
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
});
