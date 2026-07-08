'use client';

import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { api } from '~/trpc/react';

export default function CongressionalRecordPage() {
    const { data, isLoading } = api.congressionalRecord.list.useQuery({
        page: 1,
        pageSize: 30,
    });

    return (
        <Box>
            <Typography variant='h4' sx={{ mb: 2 }}>
                Congressional Record
            </Typography>
            <Typography variant='body1' color='text.secondary' sx={{ mb: 3 }}>
                Browse daily transcripts of Congressional debates, speeches, and proceedings.
            </Typography>

            <Paper variant='outlined'>
                {isLoading ? (
                    <Box sx={{ p: 2 }}>
                        {Array.from({ length: 10 }).map((_, i) => (
                            <Skeleton key={`skeleton-${i}`} height={60} sx={{ mb: 1 }} />
                        ))}
                    </Box>
                ) : (
                    <List disablePadding>
                        {data?.issues?.map((issue) => {
                            const dateStr = issue.issue_date
                                ? new Date(issue.issue_date).toLocaleDateString('en-US', {
                                    weekday: 'long',
                                    year: 'numeric',
                                    month: 'long',
                                    day: 'numeric',
                                })
                                : 'Unknown Date';

                            const sectionCounts: Record<string, number> = {};
                            for (const g of issue.crec_granule) {
                                const s = g.section ?? 'Other';
                                sectionCounts[s] = (sectionCounts[s] ?? 0) + 1;
                            }

                            return (
                                <ListItem key={issue.crec_issue_id} disablePadding divider>
                                    <ListItemButton
                                        component={Link}
                                        href={`/congress/record/${issue.crec_issue_id}`}
                                    >
                                        <ListItemText
                                            primary={dateStr}
                                            secondary={
                                                <Box
                                                    component='span'
                                                    sx={{
                                                        display: 'flex',
                                                        gap: 1,
                                                        mt: 0.5,
                                                    }}
                                                >
                                                    {Object.entries(sectionCounts).map(
                                                        ([section, count]) => (
                                                            <Chip
                                                                key={section}
                                                                label={`${section}: ${count}`}
                                                                size='small'
                                                                variant='outlined'
                                                            />
                                                        ),
                                                    )}
                                                </Box>
                                            }
                                        />
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                        {data?.issues?.length === 0 && (
                            <ListItem>
                                <ListItemText primary='No Congressional Record issues found.' />
                            </ListItem>
                        )}
                    </List>
                )}
            </Paper>
        </Box>
    );
}
