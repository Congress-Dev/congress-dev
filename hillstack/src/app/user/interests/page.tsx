'use client';

import AddIcon from '@mui/icons-material/Add';
import AutorenewIcon from '@mui/icons-material/Autorenew';
import CheckBoxIcon from '@mui/icons-material/CheckBox';
import CheckBoxOutlineBlankIcon from '@mui/icons-material/CheckBoxOutlineBlank';
import {
	Alert,
	Box,
	Button,
	Chip,
	CircularProgress,
	Container,
	Divider,
	IconButton,
	Paper,
	TextField,
	Tooltip,
	Typography,
} from '@mui/material';
import { useSession } from 'next-auth/react';
import { type ChangeEvent, useEffect, useMemo, useState } from 'react';
import { api } from '~/trpc/react';

type MatchItem = {
	user_interest_usc_content_id: number;
	usc_ident: string | null;
	match_source: string | null;
	is_active: boolean | null;
	match_rank: number | null;
};

// Group matched sections by USC title (e.g. "t42" → "Title 42")
function groupByTitle(matches: MatchItem[]): Record<string, MatchItem[]> {
	const groups: Record<string, MatchItem[]> = {};
	for (const m of matches) {
		const parts = m.usc_ident?.split('/') ?? [];
		// usc_ident looks like /us/usc/t42/s1395/...
		const titlePart = parts[3] ?? 'unknown';
		const titleNum = titlePart.replace('t', 'Title ');
		if (!groups[titleNum]) groups[titleNum] = [];
		groups[titleNum].push(m);
	}
	return groups;
}

export default function InterestsPage() {
	const { data: session, status } = useSession();
	const utils = api.useUtils();

	const { data: interest, isLoading } = api.user.interestGet.useQuery(
		undefined,
		{ enabled: Boolean(session) },
	);

	const [text, setText] = useState('');
	const [addIdent, setAddIdent] = useState('');
	const [showAddField, setShowAddField] = useState(false);

	useEffect(() => {
		if (interest?.interest_text) {
			setText(interest.interest_text);
		}
	}, [interest?.interest_text]);

	const saveMutation = api.user.interestSave.useMutation({
		onSuccess: () => utils.user.interestGet.invalidate(),
	});

	const toggleMutation = api.user.interestToggleSection.useMutation({
		onSuccess: () => utils.user.interestGet.invalidate(),
	});

	const addMutation = api.user.interestAddSection.useMutation({
		onSuccess: () => {
			utils.user.interestGet.invalidate();
			setAddIdent('');
			setShowAddField(false);
		},
	});

	const sectionHeadings: Record<string, string> =
		interest?.sectionHeadings ?? {};

	const rawMatches: MatchItem[] = (
		interest?.user_interest_usc_content ?? []
	).map((m) => ({
		user_interest_usc_content_id: m.user_interest_usc_content_id,
		usc_ident: m.usc_ident ?? null,
		match_source: m.match_source ?? null,
		is_active: m.is_active ?? null,
		match_rank: m.match_rank ?? null,
	}));

	const grouped = useMemo(
		() => groupByTitle(rawMatches),
		// eslint-disable-next-line react-hooks/exhaustive-deps
		[interest?.user_interest_usc_content],
	);

	const activeCount = rawMatches.filter((m) => m.is_active).length;

	if (status === 'loading') {
		return (
			<Container maxWidth='md' sx={{ py: 4 }}>
				<CircularProgress />
			</Container>
		);
	}

	if (!session) {
		return (
			<Container maxWidth='md' sx={{ py: 4 }}>
				<Alert severity='info'>
					Please log in to manage your policy interests.
				</Alert>
			</Container>
		);
	}

	return (
		<Container maxWidth='md' sx={{ py: 4 }}>
			<Typography gutterBottom variant='h1'>
				Your Policy Interests
			</Typography>
			<Typography color='textSecondary' sx={{ mb: 3 }} variant='body2'>
				Describe what policy areas you care about in plain language. The
				system will find matching US Code sections and alert you when
				new legislation touches them.
			</Typography>

			<Paper elevation={2} sx={{ p: 3, mb: 3 }}>
				<TextField
					fullWidth
					helperText='Be specific for better matches. Up to 500 characters.'
					label='What policy areas do you care about?'
					maxRows={6}
					minRows={3}
					multiline
					onChange={(e: ChangeEvent<HTMLInputElement>) =>
						setText(e.target.value.slice(0, 500))
					}
					placeholder='e.g. "Medicare billing and reimbursement policy for rural critical access hospitals"'
					value={text}
				/>
				<Box
					sx={{
						mt: 2,
						display: 'flex',
						alignItems: 'center',
						gap: 1,
					}}
				>
					<Button
						disabled={
							!text.trim() ||
							saveMutation.isPending ||
							text === interest?.interest_text
						}
						onClick={() =>
							saveMutation.mutate({ interest_text: text })
						}
						startIcon={
							saveMutation.isPending ? (
								<CircularProgress size={16} />
							) : (
								<AutorenewIcon />
							)
						}
						variant='contained'
					>
						{saveMutation.isPending
							? 'Finding matches…'
							: interest?.interest_text
								? 'Update interests'
								: 'Find matching sections'}
					</Button>
					{saveMutation.isError && (
						<Typography color='error' variant='caption'>
							Failed to save. Please try again.
						</Typography>
					)}
				</Box>
			</Paper>

			{isLoading && <CircularProgress />}

			{interest && rawMatches.length > 0 && (
				<Paper elevation={2} sx={{ p: 3 }}>
					<Box
						sx={{
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'space-between',
							mb: 2,
						}}
					>
						<Typography variant='h2'>
							Matched US Code Sections
						</Typography>
						<Chip
							label={`${activeCount} active`}
							size='small'
							variant='outlined'
						/>
					</Box>

					{(Object.entries(grouped) as [string, MatchItem[]][]).map(
						([titleLabel, sections]) => (
							<Box key={titleLabel} sx={{ mb: 2 }}>
								<Typography
									color='textSecondary'
									sx={{ mb: 0.5 }}
									variant='subtitle2'
								>
									{titleLabel}
								</Typography>
								{sections.map((match) => {
									const sectionSlug =
										match.usc_ident
											?.split('/')
											.slice(3)
											.join('/') ?? '';
									const heading = match.usc_ident
										? sectionHeadings[match.usc_ident]
										: undefined;
									return (
										<Box
											key={
												match.user_interest_usc_content_id
											}
											sx={{
												display: 'flex',
												alignItems: 'center',
												py: 0.5,
												opacity: match.is_active
													? 1
													: 0.45,
											}}
										>
											<Tooltip
												title={
													match.is_active
														? 'Click to deselect this section'
														: 'Click to restore this section'
												}
											>
												<IconButton
													onClick={() =>
														toggleMutation.mutate({
															user_interest_usc_content_id:
																match.user_interest_usc_content_id,
															is_active:
																!match.is_active,
														})
													}
													size='small'
													sx={{ mr: 1 }}
												>
													{match.is_active ? (
														<CheckBoxIcon
															color='primary'
															fontSize='small'
														/>
													) : (
														<CheckBoxOutlineBlankIcon fontSize='small' />
													)}
												</IconButton>
											</Tooltip>
											<Typography
												sx={{
													fontFamily: 'monospace',
													flexShrink: 0,
												}}
												variant='body2'
											>
												{sectionSlug}
											</Typography>
											{heading && (
												<Typography
													color='textSecondary'
													sx={{
														ml: 1,
														overflow: 'hidden',
														textOverflow:
															'ellipsis',
														whiteSpace: 'nowrap',
													}}
													variant='body2'
												>
													— {heading}
												</Typography>
											)}
											{match.match_source ===
												'manual' && (
												<Chip
													label='manual'
													size='small'
													sx={{
														ml: 1,
														flexShrink: 0,
													}}
													variant='outlined'
												/>
											)}
										</Box>
									);
								})}
								<Divider sx={{ mt: 1 }} />
							</Box>
						),
					)}

					<Box sx={{ mt: 2 }}>
						{showAddField ? (
							<Box sx={{ display: 'flex', gap: 1 }}>
								<TextField
									label='USC citation'
									onChange={(
										e: ChangeEvent<HTMLInputElement>,
									) => setAddIdent(e.target.value)}
									placeholder='/us/usc/t42/s1395'
									size='small'
									value={addIdent}
								/>
								<Button
									disabled={
										!addIdent.trim() ||
										addMutation.isPending
									}
									onClick={() =>
										addMutation.mutate({
											usc_ident: addIdent,
										})
									}
									variant='contained'
								>
									Add
								</Button>
								<Button
									onClick={() => setShowAddField(false)}
									variant='outlined'
								>
									Cancel
								</Button>
							</Box>
						) : (
							<Button
								onClick={() => setShowAddField(true)}
								size='small'
								startIcon={<AddIcon />}
								variant='text'
							>
								Add section manually
							</Button>
						)}
					</Box>
				</Paper>
			)}

			{interest && rawMatches.length === 0 && !isLoading && (
				<Alert severity='info'>
					No matching sections found. Try a more specific interest
					description, or make sure ChromaDB has been indexed.
				</Alert>
			)}
		</Container>
	);
}
