'use client';

import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { api } from '~/trpc/react';

export default function BillDebatesPage() {
    const params = useParams();
    const billId = Number(params.billId);

    const { data, isLoading } = api.congressionalRecord.debatesForBill.useQuery({
        legislationId: billId,
    });

    if (isLoading) {
        return (
            <Box sx={{ p: 2 }}>
                {Array.from({ length: 5 }).map((_, i) => (
                    <Skeleton key={`skeleton-${i}`} height={120} sx={{ mb: 2 }} />
                ))}
            </Box>
        );
    }

    if (!data || data.length === 0) {
        return (
            <Box sx={{ p: 3, textAlign: 'center' }}>
                <Typography color='text.secondary'>
                    No Congressional Record debates found referencing this bill.
                </Typography>
            </Box>
        );
    }

    // Group by granule for better display
    const byGranule = new Map<number, {
        granuleId: number;
        issueId: number;
        title: string;
        section: string | null;
        issueDate: Date | null;
        speeches: typeof data;
    }>();

    for (const ref of data) {
        const speech = ref.crec_speech;
        if (!speech?.crec_granule) continue;
        const gId = speech.crec_granule.crec_granule_id;
        if (!byGranule.has(gId)) {
            byGranule.set(gId, {
                granuleId: gId,
                issueId: speech.crec_granule.crec_issue_id ?? 0,
                title: speech.crec_granule.title ?? 'Untitled Debate',
                section: speech.crec_granule.section,
                issueDate: speech.crec_granule.crec_issue?.issue_date ?? null,
                speeches: [],
            });
        }
        byGranule.get(gId)?.speeches.push(ref);
    }

    return (
        <Box>
            <Typography variant='body2' color='text.secondary' sx={{ mb: 2 }}>
                {data.length} mention{data.length !== 1 ? 's' : ''} found in the Congressional Record
            </Typography>

            {Array.from(byGranule.values()).map((group) => {
                const dateStr = group.issueDate
                    ? new Date(group.issueDate).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                    })
                    : '';

                return (
                    <Paper key={group.granuleId} variant='outlined' sx={{ p: 2, mb: 2 }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
                            <Link
                                href={`/congress/record/${group.issueId}/${group.granuleId}`}
                                style={{ textDecoration: 'none', color: 'inherit' }}
                            >
                                <Typography variant='subtitle1' fontWeight='bold'>
                                    {group.title}
                                </Typography>
                            </Link>
                            {group.section && (
                                <Chip label={group.section} size='small' variant='outlined' />
                            )}
                            {dateStr && (
                                <Typography variant='caption' color='text.secondary'>
                                    {dateStr}
                                </Typography>
                            )}
                        </Box>

                        {group.speeches.slice(0, 3).map((ref) => {
                            const speech = ref.crec_speech;
                            if (!speech) return null;
                            const leg = speech.legislator;
                            const name = leg
                                ? `${leg.first_name ?? ''} ${leg.last_name ?? ''}`.trim()
                                : speech.speaker_raw ?? 'Unknown';

                            return (
                                <Box
                                    key={speech.crec_speech_id}
                                    sx={{
                                        display: 'flex',
                                        gap: 1.5,
                                        mb: 1,
                                        p: 1,
                                        borderRadius: 1,
                                        bgcolor: 'action.hover',
                                    }}
                                >
                                    <Avatar sx={{ width: 28, height: 28, fontSize: 14 }}>
                                        {name[0] ?? '?'}
                                    </Avatar>
                                    <Box sx={{ flex: 1, minWidth: 0 }}>
                                        <Typography variant='caption' fontWeight='bold'>
                                            {name}
                                            {leg?.party ? ` (${leg.party})` : ''}
                                        </Typography>
                                        <Typography
                                            variant='body2'
                                            sx={{
                                                display: '-webkit-box',
                                                WebkitLineClamp: 3,
                                                WebkitBoxOrient: 'vertical',
                                                overflow: 'hidden',
                                            }}
                                        >
                                            {speech.content_text}
                                        </Typography>
                                    </Box>
                                </Box>
                            );
                        })}

                        {group.speeches.length > 3 && (
                            <Link
                                href={`/congress/record/${group.issueId}/${group.granuleId}`}
                            >
                                <Typography variant='caption' color='primary'>
                                    View all {group.speeches.length} mentions in this debate
                                </Typography>
                            </Link>
                        )}
                    </Paper>
                );
            })}
        </Box>
    );
}
