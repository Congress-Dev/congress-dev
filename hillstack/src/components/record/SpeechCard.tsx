import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import type { inferRouterOutputs } from '@trpc/server';
import type { AppRouter } from '~/server/api/root';

type GranuleOutput = inferRouterOutputs<AppRouter>['congressionalRecord']['getGranule'];
type SpeechType = GranuleOutput['crec_speech'][number];

function getPartyColor(party: string | null | undefined): string {
    if (!party) return 'default';
    const p = party.toLowerCase();
    if (p.startsWith('r')) return '#e53935';
    if (p.startsWith('d')) return '#1e88e5';
    return '#9e9e9e';
}

export function SpeechCard({ speech }: { speech: SpeechType }) {
    const legislator = speech.legislator;
    const speakerName = legislator
        ? `${legislator.first_name ?? ''} ${legislator.last_name ?? ''}`.trim()
        : speech.speaker_raw || 'Unknown Speaker';

    const partyColor = getPartyColor(legislator?.party);

    return (
        <Paper
            variant='outlined'
            sx={{ p: 2, mb: 2 }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1.5 }}>
                {legislator?.image_url ? (
                    <Avatar
                        src={legislator.image_url}
                        alt={speakerName}
                        sx={{ width: 36, height: 36 }}
                    />
                ) : (
                    <Avatar sx={{ width: 36, height: 36, bgcolor: partyColor }}>
                        {speakerName[0] ?? '?'}
                    </Avatar>
                )}

                <Box sx={{ flex: 1 }}>
                    {speech.legislator_bioguide_id ? (
                        <Link
                            href={`/congress/legislators/${speech.legislator_bioguide_id}`}
                            style={{ textDecoration: 'none', color: 'inherit' }}
                        >
                            <Typography variant='subtitle2' fontWeight='bold'>
                                {speakerName}
                            </Typography>
                        </Link>
                    ) : (
                        <Typography variant='subtitle2' fontWeight='bold'>
                            {speakerName}
                        </Typography>
                    )}
                    {legislator && (
                        <Typography variant='caption' color='text.secondary'>
                            {legislator.party ?? ''} - {legislator.state ?? ''}
                        </Typography>
                    )}
                </Box>

                {speech.word_count != null && (
                    <Chip
                        label={`${speech.word_count.toLocaleString()} words`}
                        size='small'
                        variant='outlined'
                    />
                )}
            </Box>

            <Typography
                variant='body2'
                sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}
            >
                {speech.content_text}
            </Typography>

            {speech.crec_bill_reference.length > 0 && (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1.5 }}>
                    {speech.crec_bill_reference.map((ref) => (
                        <Tooltip
                            key={ref.crec_bill_reference_id}
                            title={ref.legislation?.title ?? 'Bill not found in database'}
                            arrow
                        >
                            {ref.legislation_id ? (
                                <Chip
                                    component={Link}
                                    href={`/congress/bills/${ref.legislation_id}/overview`}
                                    label={ref.cite_text}
                                    size='small'
                                    color='primary'
                                    variant='outlined'
                                    clickable
                                />
                            ) : (
                                <Chip
                                    label={ref.cite_text}
                                    size='small'
                                    variant='outlined'
                                />
                            )}
                        </Tooltip>
                    ))}
                </Box>
            )}
        </Paper>
    );
}
