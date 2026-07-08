'use client';

import ArticleOutlinedIcon from '@mui/icons-material/ArticleOutlined';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { api } from '~/trpc/react';

export function LegislatorSpeakingStats({
    bioguideId,
}: {
    bioguideId: string;
}) {
    const { data, isLoading } = api.congressionalRecord.legislatorStats.useQuery({
        bioguideId,
    });

    if (isLoading || !data || data.speechCount === 0) {
        return null;
    }

    return (
        <Card variant='outlined' sx={{ mt: 2 }}>
            <Toolbar
                disableGutters
                sx={{
                    px: 2,
                    height: '35px',
                    minHeight: '35px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                }}
                variant='dense'
            >
                <ArticleOutlinedIcon sx={{ fontSize: 16 }} />
                Congressional Record Activity
            </Toolbar>
            <Box sx={{ px: 2, py: 1.5 }}>
                <Box sx={{ display: 'flex', gap: 2, mb: 1.5, flexWrap: 'wrap' }}>
                    <Box>
                        <Typography variant='h5' fontWeight='bold'>
                            {data.totalWords.toLocaleString()}
                        </Typography>
                        <Typography variant='caption' color='text.secondary'>
                            Total Words
                        </Typography>
                    </Box>
                    <Box>
                        <Typography variant='h5' fontWeight='bold'>
                            {data.speechCount.toLocaleString()}
                        </Typography>
                        <Typography variant='caption' color='text.secondary'>
                            Speeches
                        </Typography>
                    </Box>
                    {data.speechCount > 0 && (
                        <Box>
                            <Typography variant='h5' fontWeight='bold'>
                                {Math.round(data.totalWords / data.speechCount).toLocaleString()}
                            </Typography>
                            <Typography variant='caption' color='text.secondary'>
                                Avg Words/Speech
                            </Typography>
                        </Box>
                    )}
                </Box>
            </Box>

            {data.recentSpeeches.length > 0 && (
                <>
                    <Toolbar
                        disableGutters
                        sx={{
                            px: 2,
                            height: '30px',
                            minHeight: '30px',
                        }}
                        variant='dense'
                    >
                        <Typography variant='caption' color='text.secondary'>
                            Recent Speeches
                        </Typography>
                    </Toolbar>
                    <List dense disablePadding>
                        {data.recentSpeeches.map((speech) => {
                            const granule = speech.crec_granule;
                            const issueDate = granule?.crec_issue?.issue_date;
                            const dateStr = issueDate
                                ? new Date(issueDate).toLocaleDateString('en-US', {
                                    month: 'short',
                                    day: 'numeric',
                                    year: 'numeric',
                                })
                                : '';

                            return (
                                <ListItem
                                    key={speech.crec_speech_id}
                                    disablePadding
                                >
                                    <ListItemButton
                                        component={Link}
                                        href={`/congress/record/${granule?.crec_issue_id}/${granule?.crec_granule_id}`}
                                    >
                                        <Box sx={{ width: '100%' }}>
                                            <Box
                                                sx={{
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                }}
                                            >
                                                <Typography
                                                    variant='body2'
                                                    sx={{
                                                        display: '-webkit-box',
                                                        WebkitLineClamp: 1,
                                                        WebkitBoxOrient: 'vertical',
                                                        overflow: 'hidden',
                                                        flex: 1,
                                                    }}
                                                >
                                                    {granule?.title ?? 'Speech'}
                                                </Typography>
                                                <Chip
                                                    label={dateStr}
                                                    size='small'
                                                    variant='outlined'
                                                    sx={{ ml: 1, flexShrink: 0 }}
                                                />
                                            </Box>
                                            <Typography
                                                variant='caption'
                                                color='text.secondary'
                                            >
                                                {speech.word_count?.toLocaleString()} words
                                            </Typography>
                                        </Box>
                                    </ListItemButton>
                                </ListItem>
                            );
                        })}
                    </List>
                </>
            )}
        </Card>
    );
}
