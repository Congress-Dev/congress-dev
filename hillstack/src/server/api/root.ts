import { billRouter } from '~/server/api/routers/bill';
import { statsRouter } from '~/server/api/routers/stats';
import { userRouter } from '~/server/api/routers/user';
import { createCallerFactory, createTRPCRouter } from '~/server/api/trpc';
import { committeeRouter } from './routers/committee';
import { legislatorRouter } from './routers/legislator';

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
	bill: billRouter,
	legislator: legislatorRouter,
	committee: committeeRouter,
	stats: statsRouter,
	user: userRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;

/**
 * Create a server-side caller for the tRPC API.
 * @example
 * const trpc = createCaller(createContext);
 * const res = await trpc.post.all();
 *       ^? Post[]
 */
export const createCaller = createCallerFactory(appRouter);
