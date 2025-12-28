import { PrismaAdapter } from '@auth/prisma-adapter';
import NextAuth from 'next-auth';
import type { GoogleProfile } from 'next-auth/providers/google';
import GoogleProvider from 'next-auth/providers/google';
import { cache } from 'react';
import { env } from '~/env';

import { db } from '~/server/db';

const {
	auth: uncachedAuth,
	handlers,
	signIn,
	signOut,
} = NextAuth({
	providers: [
		GoogleProvider({
			clientId: env.GOOGLE_CLIENT_ID,
			clientSecret: env.GOOGLE_CLIENT_SECRET,
		}),
	],
	adapter: PrismaAdapter(db),
	callbacks: {
		async signIn({ user, account, profile }) {
			const googleProfile = profile as GoogleProfile;
			if (
				account?.provider === 'google' &&
				googleProfile?.picture &&
				!user.image
			) {
				try {
					const res = await fetch(googleProfile.picture);
					const buffer = Buffer.from(await res.arrayBuffer());
					const base64 = `data:image/jpeg;base64,${buffer.toString('base64')}`;

					await db.user.update({
						where: { id: user.id },
						data: { image: base64 },
					});
				} catch (err) {
					console.error('Failed to cache avatar', err);
				}
			}
			return true;
		},
		session: ({ session, user }) => ({
			...session,
			user: {
				...session.user,
				id: user.id,
			},
		}),
	},
});

const auth = cache(uncachedAuth);

export { auth, handlers, signIn, signOut };
