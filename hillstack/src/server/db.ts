import { PrismaPg } from '@prisma/adapter-pg';
import { env } from '~/env';
import { PrismaClient } from 'generated/prisma/client';

const createPrismaClient = () => {
	const connectionString = `${process.env.DATABASE_URL}`;
	const adapter = new PrismaPg({ connectionString });
	const prisma = new PrismaClient({ adapter });

	return prisma;
};

const globalForPrisma = globalThis as unknown as {
	prisma: ReturnType<typeof createPrismaClient> | undefined;
};

export const db = globalForPrisma.prisma ?? createPrismaClient();

if (env.NODE_ENV !== 'production') globalForPrisma.prisma = db;
