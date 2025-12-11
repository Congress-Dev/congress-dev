import { Box, Chip, Container, Paper, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { api, HydrateClient } from '~/trpc/server';

export default async function LegislatorPage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { bioguideId } = await params;
	const data = await api.legislator.get({
		bioguideId: bioguideId as string,
	});

	return (
		<HydrateClient>
			<Container maxWidth='xl'>{data.first_name}</Container>
		</HydrateClient>
	);
}
