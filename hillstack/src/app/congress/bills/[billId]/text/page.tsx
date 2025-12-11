import InfoOutlineIcon from '@mui/icons-material/InfoOutline';
import { Box, Card, Toolbar, Tooltip, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import { BillVersionEnum } from '~/enums';
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

	const latestVersion =
		data.legislation_version[data.legislation_version.length - 1];

	const parentMap: { [k: number]: number } = {};

	return (
		<Box sx={{ display: 'flex', gap: 3 }}>
			<Box sx={{ flex: 1 }}>
				<Card variant='outlined'>
					<Toolbar
						disableGutters
						sx={{
							height: '30px',
							minHeight: '30px',
							px: 2,
							display: 'flex',
						}}
						variant='dense'
					>
						{BillVersionEnum[latestVersion?.legislation_version]}
					</Toolbar>
					<Box sx={{ py: 3, pr: 3 }}>
						{latestVersion?.legislation_content.map((content) => {
							if (
								!content.parent_id ||
								parentMap[content.parent_id] == null
							) {
								parentMap[content.legislation_content_id] = 0;
							} else if (content.parent_id) {
								parentMap[content.legislation_content_id] =
									(parentMap[content.parent_id] ?? 0) + 1;
							}

							const indent =
								parentMap[content.legislation_content_id] ?? 0;

							const sectionHeading =
								// content.section_display?.match(/^\d\./);
								indent === 1;

							const sectionSummary =
								content.legislation_content_summary
									.map((summary) => summary.summary)
									.join(' ');

							return content.heading?.length ||
								content.content_str?.length ? (
								<Box
									key={content.legislation_content_id}
									sx={{
										ml: indent * 3,
									}}
								>
									<Box
										sx={{
											display: 'flex',
											alignItems: 'center',
										}}
									>
										{sectionHeading &&
										sectionSummary.length ? (
											<Tooltip
												arrow
												placement='right-start'
												title={sectionSummary}
											>
												<InfoOutlineIcon
													color='primary'
													sx={{
														fontSize: '18px',
														mr: 1,
													}}
												/>
											</Tooltip>
										) : null}
										<Box sx={{ display: 'flex' }}>
											<Typography
												sx={{ mr: 0.5 }}
												variant={'subtitle2'}
												{...(sectionHeading
													? { color: 'primary' }
													: {})}
											>
												{content.section_display}
											</Typography>
											<Typography
												sx={{ flex: 1 }}
												variant={
													sectionHeading
														? 'subtitle2'
														: 'subtitle1'
												}
												{...(sectionHeading
													? { color: 'primary' }
													: {})}
											>
												{content.heading ??
													content.content_str}
											</Typography>
										</Box>
									</Box>
									{content.heading && (
										<Typography sx={{ ml: 3 }}>
											{content.content_str}
										</Typography>
									)}
								</Box>
							) : null;
						})}
					</Box>
				</Card>
			</Box>
			<Box sx={{ width: '300px', display: { xs: 'none', md: 'block' } }}>
				test
			</Box>
		</Box>
	);
}
