'use client';

import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Chip from '@mui/material/Chip';
import Paper from '@mui/material/Paper';
import Skeleton from '@mui/material/Skeleton';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { api } from '~/trpc/react';

function getPartyColor(party: string | null | undefined): string {
    if (!party) return '#9e9e9e';
    const p = party.toLowerCase();
    if (p.startsWith('r')) return '#e53935';
    if (p.startsWith('d')) return '#1e88e5';
    return '#9e9e9e';
}

export default function SpeakerStatsPage() {
    const { data, isLoading } = api.congressionalRecord.speakerStats.useQuery({
        limit: 50,
        page: 1,
    });

    return (
        <Box>
            <Typography variant='h4' sx={{ mb: 1 }}>
                Speaker Statistics
            </Typography>
            <Typography variant='body1' color='text.secondary' sx={{ mb: 3 }}>
                Top Congressional speakers by total word count in the Congressional Record.
            </Typography>

            <TableContainer component={Paper} variant='outlined'>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Rank</TableCell>
                            <TableCell>Legislator</TableCell>
                            <TableCell>Party</TableCell>
                            <TableCell>State</TableCell>
                            <TableCell align='right'>Total Words</TableCell>
                            <TableCell align='right'>Speeches</TableCell>
                            <TableCell align='right'>Avg Words/Speech</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {isLoading
                            ? Array.from({ length: 20 }).map((_, i) => (
                                <TableRow key={`skeleton-${i}`}>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                    <TableCell><Skeleton /></TableCell>
                                </TableRow>
                            ))
                            : data?.speakers?.map((speaker, idx) => {
                                const avg = speaker.speech_count > 0
                                    ? Math.round(speaker.total_words / speaker.speech_count)
                                    : 0;

                                return (
                                    <TableRow key={speaker.bioguide_id} hover>
                                        <TableCell>{idx + 1}</TableCell>
                                        <TableCell>
                                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                                {speaker.image_url ? (
                                                    <Avatar
                                                        src={speaker.image_url}
                                                        sx={{ width: 32, height: 32 }}
                                                    />
                                                ) : (
                                                    <Avatar
                                                        sx={{
                                                            width: 32,
                                                            height: 32,
                                                            bgcolor: getPartyColor(speaker.party),
                                                        }}
                                                    >
                                                        {(speaker.first_name?.[0] ?? '') +
                                                            (speaker.last_name?.[0] ?? '')}
                                                    </Avatar>
                                                )}
                                                <Link
                                                    href={`/congress/legislators/${speaker.bioguide_id}`}
                                                    style={{
                                                        textDecoration: 'none',
                                                        color: 'inherit',
                                                    }}
                                                >
                                                    {speaker.first_name} {speaker.last_name}
                                                </Link>
                                            </Box>
                                        </TableCell>
                                        <TableCell>
                                            <Chip
                                                label={speaker.party ?? 'Unknown'}
                                                size='small'
                                                sx={{
                                                    bgcolor: getPartyColor(speaker.party),
                                                    color: 'white',
                                                }}
                                            />
                                        </TableCell>
                                        <TableCell>{speaker.state ?? '-'}</TableCell>
                                        <TableCell align='right'>
                                            {speaker.total_words.toLocaleString()}
                                        </TableCell>
                                        <TableCell align='right'>
                                            {speaker.speech_count.toLocaleString()}
                                        </TableCell>
                                        <TableCell align='right'>
                                            {avg.toLocaleString()}
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                    </TableBody>
                </Table>
            </TableContainer>

            {!isLoading && data?.speakers?.length === 0 && (
                <Typography color='text.secondary' sx={{ mt: 2, textAlign: 'center' }}>
                    No speaker data available yet. Run the Congressional Record importer first.
                </Typography>
            )}
        </Box>
    );
}
