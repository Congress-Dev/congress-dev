import {
	Box,
	Card,
	CardActionArea,
	CardContent,
	Typography,
} from '@mui/material';
import Link from 'next/link';
import { api } from '~/trpc/server';

export default async function USCodePage() {
	const releases = await api.uscode.releases();

	return (
		<Box>
			<Typography gutterBottom variant='h5'>
				United States Code
			</Typography>
			<Typography color='text.secondary' sx={{ mb: 3 }} variant='body2'>
				Release points of the US Code, typically aligned around the
				passage of major legislation.
			</Typography>
			<Box
				sx={{
					display: 'grid',
					gridTemplateColumns: {
						xs: '1fr',
						sm: '1fr 1fr',
						md: '1fr 1fr 1fr',
					},
					gap: 2,
				}}
			>
				{releases.map((release) => (
					<Card key={release.usc_release_id} variant='outlined'>
						<CardActionArea
							component={Link}
							href={`/congress/uscode/${release.usc_release_id}`}
						>
							<CardContent>
								<Typography variant='h6'>
									{release.short_title}
								</Typography>
								{release.long_title && (
									<Typography
										color='text.secondary'
										sx={{ fontStyle: 'italic' }}
										variant='body2'
									>
										{release.long_title}
									</Typography>
								)}
								<Typography
									color='text.secondary'
									sx={{ mt: 1 }}
									variant='body2'
								>
									Effective:{' '}
									{release.effective_date
										? new Date(
												release.effective_date,
											).toLocaleDateString()
										: 'N/A'}
								</Typography>
							</CardContent>
						</CardActionArea>
					</Card>
				))}
			</Box>
		</Box>
	);
}
