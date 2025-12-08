import { Prisma } from "generated/prisma/client";
import { legislatorjob } from "generated/prisma/enums";
import { z } from "zod";
import { createTRPCRouter, publicProcedure } from "~/server/api/trpc";

export const legislatorRouter = createTRPCRouter({
    search: publicProcedure
        .input(
            z.object({
                query: z.optional(z.string()),
                congress: z.optional(z.array(z.number())),
                chamber: z.optional(z.array(z.string())),
                page: z.number(),
                pageSize: z.number(),
            }),
        )
        .query(async ({ input, ctx }) => {
            const { query, congress, chamber, page, pageSize } = input;

            const jobLookup: { [key: string]: legislatorjob } = {
                House: "Representative",
                Senate: "Senator",
            };

            const where = {
                ...(congress
                    ? {
                          congress_id: { hasSome: congress },
                      }
                    : {}),
                ...(chamber
                    ? {
                          job: {
                              in: chamber
                                  .map((c) => jobLookup[c])
                                  .filter((c) => c != null),
                          },
                      }
                    : {}),
                ...(query
                    ? {
                          OR: [
                              {
                                  first_name: {
                                      contains: query,
                                      mode: Prisma.QueryMode.insensitive,
                                  },
                              },
                              {
                                  last_name: {
                                      search: query,
                                      mode: Prisma.QueryMode.insensitive,
                                  },
                              },
                          ],
                      }
                    : {}),
            };

            const totalResults = await ctx.db.legislator.count({
                where,
            });

            const members = await ctx.db.legislator.findMany({
                select: {
                    first_name: true,
                    last_name: true,
                    party: true,
                    state: true,
                    district: true,
                    image_url: true,
                    bioguide_id: true,
                    job: true,
                },
                where,
                orderBy: [{ last_name: "asc" }, { first_name: "asc" }],
                skip: (page - 1) * pageSize,
                take: pageSize,
            });

            return {
                members,
                totalResults,
            };
        }),
});
