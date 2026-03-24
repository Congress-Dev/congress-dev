import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Divider from '@mui/material/Divider';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { api } from '~/trpc/server';
import { HydrateClient } from '~/trpc/server';

export default async function IssuePage({
    params,
}: {
    params: Promise<{ issueId: string }>;
}) {
    const { issueId } = await params;
    const issue = await api.congressionalRecord.getIssue({
        issueId: Number(issueId),
    });

    const dateStr = issue.issue_date
        ? new Date(issue.issue_date).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
        })
        : 'Unknown Date';

    const sections = ['Senate', 'House', 'Extensions', 'DailyDigest'] as const;
    const granulesBySection: Record<string, typeof issue.crec_granule> = {};
    for (const g of issue.crec_granule) {
        const s = g.section ?? 'Other';
        if (!granulesBySection[s]) granulesBySection[s] = [];
        granulesBySection[s].push(g);
    }

    return (
        <HydrateClient>
            <Box>
                <Typography variant='h4' sx={{ mb: 1 }}>
                    Congressional Record
                </Typography>
                <Typography variant='h6' color='text.secondary' sx={{ mb: 3 }}>
                    {dateStr}
                </Typography>

                {issue.crec_summary.length > 0 && (
                    <Paper variant='outlined' sx={{ p: 2, mb: 3, bgcolor: 'action.hover' }}>
                        <Typography variant='subtitle2' color='text.secondary' sx={{ mb: 1 }}>
                            AI Summary
                        </Typography>
                        {issue.crec_summary.map((s, i) => (
                            <Typography key={`summary-${i}`} variant='body2'>
                                {s.summary}
                            </Typography>
                        ))}
                    </Paper>
                )}

                <Grid container spacing={3}>
                    {sections.map((section) => {
                        const granules = granulesBySection[section];
                        if (!granules || granules.length === 0) return null;

                        return (
                            <Grid size={{ xs: 12, md: 6 }} key={section}>
                                <Paper variant='outlined' sx={{ p: 2 }}>
                                    <Typography variant='h6' sx={{ mb: 2 }}>
                                        {section === 'DailyDigest'
                                            ? 'Daily Digest'
                                            : section === 'Extensions'
                                                ? 'Extensions of Remarks'
                                                : section}
                                    </Typography>
                                    <Divider sx={{ mb: 2 }} />
                                    {granules.map((g) => (
                                        <Box
                                            key={g.crec_granule_id}
                                            component={Link}
                                            href={`/congress/record/${issueId}/${g.crec_granule_id}`}
                                            sx={{
                                                display: 'block',
                                                p: 1.5,
                                                mb: 1,
                                                borderRadius: 1,
                                                textDecoration: 'none',
                                                color: 'inherit',
                                                '&:hover': {
                                                    bgcolor: 'action.hover',
                                                },
                                            }}
                                        >
                                            <Typography variant='body2' fontWeight='bold'>
                                                {g.title || 'Untitled'}
                                            </Typography>
                                            <Box
                                                sx={{
                                                    display: 'flex',
                                                    gap: 1,
                                                    mt: 0.5,
                                                    alignItems: 'center',
                                                }}
                                            >
                                                {g.page_start && (
                                                    <Chip
                                                        label={`pp. ${g.page_start}${g.page_end ? `-${g.page_end}` : ''}`}
                                                        size='small'
                                                        variant='outlined'
                                                    />
                                                )}
                                                <Chip
                                                    label={`${g._count.crec_speech} speeches`}
                                                    size='small'
                                                    variant='outlined'
                                                />
                                            </Box>
                                            {g.crec_summary[0]?.summary && (
                                                <Typography
                                                    variant='caption'
                                                    color='text.secondary'
                                                    sx={{
                                                        mt: 1,
                                                        display: '-webkit-box',
                                                        WebkitLineClamp: 2,
                                                        WebkitBoxOrient: 'vertical',
                                                        overflow: 'hidden',
                                                    }}
                                                >
                                                    {g.crec_summary[0].summary}
                                                </Typography>
                                            )}
                                        </Box>
                                    ))}
                                </Paper>
                            </Grid>
                        );
                    })}
                </Grid>
            </Box>
        </HydrateClient>
    );
}
