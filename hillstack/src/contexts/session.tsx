'use client';

import { SessionProvider } from 'next-auth/react';
import type { ReactNode } from 'react';

export function SessionContext(props: { children: ReactNode }) {
	return <SessionProvider>{props.children}</SessionProvider>;
}
