'use client';

import { LinearProgress } from '@mui/material';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import List from '@mui/material/List';
import Pagination from '@mui/material/Pagination';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import type React from 'react';
import { Children } from 'react';
import { Toolbar } from '~/components/toolbar';
import { useOmniSearchContext } from '~/contexts';
import { OmniSearchBox } from './omniSearchBox';

export interface OmniSearchProps {
	results: number;
	isLoading: boolean;
	children: React.ReactNode;
}

export function OmniSearch({ results, isLoading, children }: OmniSearchProps) {
	const {
		page,
		setPage,
		pageSize,
		query,
		setQuery,
		filters,
		tags,
		removeTag,
	} = useOmniSearchContext();

	return (
		<Box sx={{ mx: { xs: 2, md: 0 } }}>
			<OmniSearchBox
				onQueryChange={setQuery}
				onRemoveTag={removeTag}
				query={query}
				tags={tags}
			/>
			<Paper elevation={1} sx={{ mb: 2 }}>
				<Box>
					<Toolbar filters={filters} results={results} />
					{isLoading && <LinearProgress />}
					<List sx={{ py: 0 }}>
						{Children.count(children) > 0 ? (
							children
						) : (
							<Box
								sx={{
									py: 4,
									display: 'flex',
									justifyContent: 'center',
								}}
							>
								<Typography variant='h2'>No Results</Typography>
							</Box>
						)}
					</List>
					{results > 0 && (
						<Box
							sx={{
								display: 'flex',
								justifyContent: 'flex-end',
								py: 1,
							}}
						>
							<Divider />
							<Pagination
								color='primary'
								count={Math.ceil(results / pageSize)}
								onChange={(_, v) => setPage(v)}
								page={page}
							/>
						</Box>
					)}
				</Box>
			</Paper>
		</Box>
	);
}
