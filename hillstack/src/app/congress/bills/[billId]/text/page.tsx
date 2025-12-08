import { Box, Container, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { api } from '~/trpc/server';

export default async function BillPage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { billId } = await params;

	const data = await api.bill.get({
		id: Number(billId as string),
	});

	const parentMap: { [k: number]: number } = {};

	return (
		<Container sx={{ maxWidth: '500px' }}>
			<Box>
				{data?.legislation_version[0]?.legislation_content.map(
					(content) => {
						if (
							!content.parent_id ||
							parentMap[content.parent_id] == null
						) {
							parentMap[content.legislation_content_id] = 0;
						} else if (
							content.parent_id &&
							parentMap[content.parent_id] != null
						) {
							parentMap[content.legislation_content_id] =
								// @ts-expect-error
								parentMap[content.parent_id] + 1;
						}

						const indent =
							parentMap[content.legislation_content_id] ?? 0;

						return (content.heading != null &&
							content.heading !== '') ||
							(content.content_str != null &&
								content.content_str !== '') ? (
							<Box
								key={content.legislation_content_id}
								sx={{ ml: indent * 2 }}
							>
								<Typography>
									{content.section_display}{' '}
									{content.heading ?? content.content_str}
								</Typography>
								{content.heading && (
									<Typography sx={{ ml: 2 }}>
										{content.content_str}
									</Typography>
								)}
							</Box>
						) : null;
					},
				)}
			</Box>
		</Container>
	);
}
