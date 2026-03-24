import Box from '@mui/material/Box';
import Breadcrumbs from '@mui/material/Breadcrumbs';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { api } from '~/trpc/server';
import { HydrateClient } from '~/trpc/server';
import { SpeechCard } from '~/components/record/SpeechCard';

export default async function GranulePage({
    params,
}: {
    params: Promise<{ issueId: string; granuleId: string }>;
}) {
    const { issueId, granuleId } = await params;
    const granule = await api.congressionalRecord.getGranule({
        granuleId: Number(granuleId),
    });

    const summary = granule.crec_summary[0]?.summary;

    return (
        <HydrateClient>
            <Box>
                <Breadcrumbs sx={{ mb: 2 }}>
                    <Link href='/congress/record'>Record</Link>
                    <Link href={`/congress/record/${issueId}`}>
                        Daily Issue
                    </Link>
                    <Typography color='text.primary'>Debate</Typography>
                </Breadcrumbs>

                <Typography variant='h5' sx={{ mb: 1 }}>
                    {granule.title || 'Congressional Record Entry'}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
                    {granule.section && (
                        <Chip label={granule.section} color='primary' size='small' />
                    )}
                    {granule.page_start && (
                        <Chip
                            label={`pp. ${granule.page_start}${granule.page_end ? `-${granule.page_end}` : ''}`}
                            size='small'
                            variant='outlined'
                        />
                    )}
                </Box>

                {summary && (
                    <Paper
                        variant='outlined'
                        sx={{ p: 2, mb: 3, bgcolor: 'action.hover' }}
                    >
                        <Typography
                            variant='subtitle2'
                            color='text.secondary'
                            sx={{ mb: 1 }}
                        >
                            AI Summary
                        </Typography>
                        <Typography variant='body2'>{summary}</Typography>
                    </Paper>
                )}

                <Typography variant='h6' sx={{ mb: 2 }}>
                    Transcript
                </Typography>

                {granule.crec_speech.map((speech) => (
                    <SpeechCard
                        key={speech.crec_speech_id}
                        speech={speech}
                    />
                ))}

                {granule.crec_speech.length === 0 && (
                    <Typography color='text.secondary'>
                        No speech segments found for this entry.
                    </Typography>
                )}
            </Box>
        </HydrateClient>
    );
}
