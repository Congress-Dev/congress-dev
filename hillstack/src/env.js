import { z } from 'zod';

const envSchema = z.object({
	DATABASE_URL: z.string().url(),
	NODE_ENV: z.enum(['development', 'test', 'production']),
	NEXT_PUBLIC_APP_URL: z.string().url(),
	AUTH_SECRET: z.string(),
	GOOGLE_CLIENT_ID: z.string(),
	GOOGLE_CLIENT_SECRET: z.string(),
});

export const env = envSchema.parse(process.env);
