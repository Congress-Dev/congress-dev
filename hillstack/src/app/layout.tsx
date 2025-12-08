import '~/styles/globals.css';

import type { Metadata } from 'next';
import { Nunito_Sans } from 'next/font/google';
import ResponsiveAppBar from '~/components/appbar';
import ThemeRegistry from '~/theme/registry';
import { TRPCReactProvider } from '~/trpc/react';

export const metadata: Metadata = {
	title: 'Congress.dev',
	description: 'Your Gateway to Understanding Federal Legislation.',
	icons: [{ rel: 'icon', url: '/favicon-32x32.png' }],
};

const nunito = Nunito_Sans({
	subsets: ['latin'],
});

export default function RootLayout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	return (
		<html lang='en'>
			<body className={nunito.className}>
				<ThemeRegistry options={{ key: 'mui' }}>
					<TRPCReactProvider>
						<ResponsiveAppBar />
						<main>
							<section></section>
							<section>{children}</section>
						</main>
					</TRPCReactProvider>
				</ThemeRegistry>
			</body>
		</html>
	);
}
