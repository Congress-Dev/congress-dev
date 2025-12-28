import FacebookIcon from '@mui/icons-material/Facebook';
import Groups2Icon from '@mui/icons-material/Groups2';
import InstagramIcon from '@mui/icons-material/Instagram';
import PlaceIcon from '@mui/icons-material/Place';
import XIcon from '@mui/icons-material/X';
import YouTubeIcon from '@mui/icons-material/YouTube';
import {
	Avatar,
	Box,
	Button,
	Card,
	Container,
	Divider,
	List,
	ListItem,
	ListItemButton,
	Toolbar,
	Typography,
} from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
import Link from 'next/link';
import { LegislatorFollow } from '~/app/congress/legislators/[bioguideId]/follow';
import { stateAbbreviations } from '~/constants';
import { api, HydrateClient } from '~/trpc/server';

interface BiographyData {
	birth?: string;
	education?: string[];
	career?: string[];
	appointment?: string;
	chairman?: string;
	viceChairman?: string;
	elected?: string;
}

interface FormattedBiographyData extends BiographyData {
	age?: number;
	birthDate?: Date;
	birthPlace?: string;
}

function capitalizeFirstLetter(string: string) {
	return string.charAt(0).toUpperCase() + string.slice(1);
}

function parseBiography(text: string | null): FormattedBiographyData {
	const bioData: BiographyData = {};
	const formattedBioData: FormattedBiographyData = {};

	if (!text) {
		return formattedBioData;
	}

	// Split the string into sentences using semicolons and trim whitespace
	const sentences = text
		.split(';')
		.map((sentence) => sentence.trim())
		.filter(Boolean);

	// Extract fields from sentences
	sentences.forEach((sentence) => {
		if (sentence.toLowerCase().includes('born')) {
			bioData.birth = sentence.replace('born in', '');
		} else if (sentence.toLowerCase().includes('graduated')) {
			bioData.education = bioData.education || [];
			bioData.education.push(sentence);
		} else if (sentence.toLowerCase().includes('attended')) {
			bioData.education = bioData.education || [];
			bioData.education.push(sentence);
		} else if (sentence.toLowerCase().includes('staff')) {
			bioData.career = bioData.career || [];
			bioData.career.push(sentence);
		} else if (sentence.toLowerCase().includes('appointed')) {
			bioData.appointment = sentence;
		} else if (sentence.toLowerCase().includes('chairman')) {
			bioData.chairman = sentence;
		} else if (sentence.toLowerCase().includes('vice chairman')) {
			bioData.viceChairman = sentence;
		} else if (sentence.toLowerCase().includes('elected')) {
			bioData.elected = sentence;
		}
	});

	if (bioData.birth) {
		const dateRegex =
			/\b((?:January|February|March|April|May|June|July|August|September|October|November|December)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec))\s*(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})\b/;
		const dateMatch = bioData.birth.match(dateRegex);

		let birthPlace = bioData.birth;
		let birthDay = null;
		if (dateMatch != null && dateMatch[0] != null) {
			birthDay = dateMatch[0];
			birthPlace = birthPlace.replace(`, ${birthDay}`, '');
		}

		formattedBioData.birthPlace = birthPlace;

		if (birthDay != null) {
			const birthDate = new Date(birthDay); // Parse the date string
			const today = new Date(); // Get today's date
			let age = today.getFullYear() - birthDate.getFullYear(); // Calculate year difference
			const monthDiff = today.getMonth() - birthDate.getMonth(); // Calculate month difference

			// Adjust age if the current month/day is before the birth month/day
			if (
				monthDiff < 0 ||
				(monthDiff === 0 && today.getDate() < birthDate.getDate())
			) {
				age--;
			}

			formattedBioData.birthDate = birthDate;
			formattedBioData.age = age;
		}
	}

	if (bioData.education) {
		formattedBioData.education = bioData.education.map((item) =>
			capitalizeFirstLetter(item),
		);
	}

	if (bioData.career) {
		formattedBioData.career = bioData.career.map((item) =>
			capitalizeFirstLetter(item),
		);
	}

	if (bioData.elected) {
		formattedBioData.elected = capitalizeFirstLetter(bioData.elected);
	}

	return {
		...bioData,
		...formattedBioData,
	};
}

export default async function LegislatorPage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { bioguideId } = await params;
	const data = await api.legislator.get({
		bioguideId: bioguideId as string,
	});

	const biographyData = parseBiography(data.profile);
	const legislation = data.legislation_sponsorship.map(
		(sponsorship) => sponsorship.legislation,
	);

	return (
		<HydrateClient>
			<Container maxWidth='xl'>
				<Box sx={{ display: { xs: 'block', md: 'flex' }, gap: 3 }}>
					<Box
						sx={{
							flexBasis: '300px',
							display: 'flex',
							flexDirection: 'column',
						}}
					>
						<Box
							sx={{
								display: 'flex',
								justifyContent: { xs: 'center', md: 'left' },
							}}
						>
							<Avatar
								src={data.image_url ?? ''}
								sx={{ width: '200px', height: '200px' }}
							/>
						</Box>
						<Box sx={{ mt: 3 }}>
							<Typography variant='h1'>{`${data.first_name} ${data.last_name}`}</Typography>
							<Typography
								color='textDisabled'
								sx={{ fontWeight: 100 }}
								variant='h2'
							>
								U.S. {data.job}
							</Typography>
						</Box>
						<Box sx={{ mt: 2, mb: 3 }}>
							<Box sx={{ display: 'flex', alignItems: 'center' }}>
								<Groups2Icon
									color='disabled'
									sx={{ fontSize: '16px', mr: 1 }}
								/>
								<Typography variant='subtitle1'>
									{data.party}
								</Typography>
							</Box>
							<Box sx={{ display: 'flex', alignItems: 'center' }}>
								<PlaceIcon
									color='disabled'
									sx={{ fontSize: '16px', mr: 1 }}
								/>
								<Typography variant='subtitle1'>
									{data?.state &&
										stateAbbreviations[
											data.state as keyof typeof stateAbbreviations
										]}
								</Typography>
							</Box>
						</Box>
						<LegislatorFollow bioguide_id={bioguideId as string} />
						<Box
							sx={{
								my: 3,
							}}
						>
							<Typography variant='subtitle1'>
								{biographyData?.elected}
							</Typography>
						</Box>
						<Divider />
						<Box
							sx={{
								mt: 3,
								display: 'flex',
								flexDirection: 'column',
								gap: 1,
							}}
						>
							{data?.twitter && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<XIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography variant='subtitle1'>
										<a
											href={`https://x.com/${data.twitter}`}
											target='_blank'
										>
											{data.twitter}
										</a>
									</Typography>
								</Box>
							)}
							{data?.facebook && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<FacebookIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography variant='subtitle1'>
										<a
											href={`https://facebook.com/${data.facebook}`}
											target='_blank'
										>
											{data.facebook}
										</a>
									</Typography>
								</Box>
							)}
							{data?.youtube && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<YouTubeIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography variant='subtitle1'>
										<a
											href={`https://youtube.com/@${data.youtube}`}
											target='_blank'
										>
											{data.youtube}
										</a>
									</Typography>
								</Box>
							)}
							{data?.instagram && (
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<InstagramIcon
										color='disabled'
										sx={{ fontSize: '16px', mr: 1 }}
									/>
									<Typography variant='subtitle1'>
										<a
											href={`https://instagram.com/${data.instagram}`}
											target='_blank'
										>
											{data.instagram}
										</a>
									</Typography>
								</Box>
							)}
						</Box>
					</Box>
					<Box sx={{ flexGrow: 1, my: { xs: 3 } }}>
						<Card variant='outlined'>
							<Toolbar
								disableGutters
								sx={{
									px: 2,
									height: '35px',
									minHeight: '35px',
									display: 'flex',
								}}
								variant='dense'
							>
								Recent Legislation
							</Toolbar>
							<List dense>
								{legislation.map((bill) => (
									<ListItem
										disablePadding
										key={bill?.legislation_id}
									>
										<ListItemButton>
											<Link
												href={`/congress/bills/${bill?.legislation_id}`}
												style={{
													width: '100%',
													display: 'block',
												}}
											>
												<Box
													sx={{
														display: 'flex',
														flexDirection: 'column',
													}}
												>
													<Typography color='primary'>
														{bill?.title}
													</Typography>
													<Typography variant='caption'>
														{`${bill?.congress?.session_number}th - `}
														{bill?.chamber ===
														'House'
															? 'H.R'
															: 'S'}
														{'. #'}
														{bill?.number}
													</Typography>
												</Box>
											</Link>
										</ListItemButton>
									</ListItem>
								))}
							</List>
						</Card>
					</Box>
				</Box>
			</Container>
		</HydrateClient>
	);
}
