import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Typography from '@mui/material/Typography';
import Link from 'next/link';
import { navigationLinks } from '~/constants';
import { HydrateClient } from '~/trpc/server';

export default async function About() {
	return (
		<HydrateClient>
			<Box sx={{ width: '100%' }}>
				<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
					<Tabs value={3}>
						{navigationLinks.map((page) => {
							const { label, href } = page;
							return (
								<Tab
									component={Link}
									href={href}
									icon={<page.icon />}
									iconPosition='start'
									key={href}
									label={label}
									sx={{ px: 2, minWidth: 50 }}
								/>
							);
						})}
					</Tabs>
				</Box>
				<Container maxWidth='xl' sx={{ pt: 3, mb: 2 }}>
					<Paper elevation={1} sx={{ p: 3 }}>
						<Box>
							<Typography variant='h1'>About Us</Typography>
							<Typography variant='subtitle2'>
								Empowering Civic Engagement and Understanding
							</Typography>
							<Box sx={{ my: 2 }}>
								This project was created to empower everyday
								people with easy access to the workings of
								Congress. We believe that democracy thrives when
								citizens are informed and engaged, but
								navigating the legislative process can feel
								overwhelming and opaque. By providing clear,
								comprehensive tools to track bills, understand
								their impact, and follow lawmakers' actions,
								this project seeks to bridge the gap between the
								public and policymaking. Our mission is to make
								federal legislation more transparent,
								accessible, and relevant to everyone—because an
								informed public is a stronger democracy.
							</Box>

							<Box>
								<Paper elevation={3} sx={{ px: 3 }}>
									<h3 className='bp5-heading'>
										Our Data Sources:
									</h3>
									<p>
										The information provided on this
										platform is sourced exclusively from
										publicly available, open-source
										government datasets, including but not
										limited to data published by the Library
										of Congress, the Government Publishing
										Office (GPO), and official Congressional
										websites such as congress.gov. These
										sources supply data on federal
										legislation, voting records, bill texts,
										and other legislative materials.
									</p>
									<p>
										This site operates as an independent
										platform that organizes, parses, and
										presents this data for public use. While
										we strive to maintain accuracy and
										up-to-date information, no warranties
										are made regarding the completeness,
										accuracy, or timeliness of the data.
										Users are encouraged to verify details
										by cross-referencing the information
										with official sources.
									</p>
									<p>
										All legislative data presented here is
										made available under applicable laws
										governing public domain content,
										ensuring it can be freely accessed and
										utilized by individuals and
										organizations. The platform does not
										claim ownership of this data and
										complies fully with all relevant usage
										terms established by the original data
										providers.
									</p>
									<ul>
										<li>
											<a
												href='https://www.govinfo.gov/bulkdata'
												rel='noopener noreferrer'
												target='_blank'
											>
												https://www.govinfo.gov/bulkdata
											</a>
											&nbsp;(Bill Text/Statuses)
										</li>
										<li>
											<a
												href='https://gpo.congress.gov/'
												rel='noopener noreferrer'
												target='_blank'
											>
												https://gpo.congress.gov/
											</a>
											&nbsp;(Bill Sponsors)
										</li>
										<li>
											<a
												href='https://uscode.house.gov/download/priorreleasepoints.htm'
												rel='noopener noreferrer'
												target='_blank'
											>
												https://uscode.house.gov/download/priorreleasepoints.htm
											</a>
											&nbsp;(USCode Text)
										</li>
										<li>
											<a
												href='https://bioguide.congress.gov/'
												rel='noopener norefferer'
												target='_blank'
											>
												https://bioguide.congress.gov/
											</a>
											&nbsp;(Member Profiles)
										</li>
										<li>
											<a
												href='https://theunitedstates.io/'
												rel='noopener norefferer'
												target='_blank'
											>
												https://theunitedstates.io/
											</a>
											&nbsp;(Member Metadata)
										</li>
										<li>
											<a
												href='https://clerk.house.gov/'
												rel='noopener norefferer'
												target='_blank'
											>
												https://clerk.house.gov/
											</a>
											&nbsp;(House Roll-Call Votes)
										</li>
										<li>
											<a
												href='https://www.senate.gov/'
												rel='noopener norefferer'
												target='_blank'
											>
												https://www.senate.gov/
											</a>
											&nbsp;(Senate Roll-Call Votes)
										</li>
									</ul>
								</Paper>
								<br />
								<Paper elevation={3} sx={{ px: 3 }}>
									<h3 className='bp5-heading'>
										Frequently Asked Questions:
									</h3>
									<ol className='faq'>
										<li>
											<b>
												How often is the data updated?
											</b>
											<br />
											We update our data regularly to
											ensure the most current information
											is available. Most updates occur in
											real time or within a few hours of
											changes being published by official
											government sources.
										</li>
										<li>
											<b>Who can use Congress.dev?</b>
											<br />
											Congress.dev is designed for
											everyone—from policy analysts,
											journalists, and developers to
											everyday citizens who want to stay
											informed about federal legislation.
										</li>
										<li>
											<b>
												Is there an API available for
												developers?
											</b>
											<br />
											Yes! Congress.dev provides a{' '}
											<a
												href='https://api.congress.dev/openapi.yaml'
												rel='noopener'
												target='_blank'
											>
												robust API
											</a>{' '}
											for developers to access legislative
											data programmatically. You can
											integrate it into your applications
											to create custom solutions or
											conduct detailed analysis.
										</li>
										<li>
											<b>Is Congress.dev free to use?</b>
											<br />
											Our core platform is free to use for
											general users.
										</li>
										<li>
											<b>
												How can I track specific bills
												or topics?
											</b>
											<br />
											You can use our search and filtering
											tools to track specific bills,
											topics, or keywords. Additionally,
											users can sign up for alerts to
											receive updates on legislation of
											interest.
										</li>
										<li>
											<b>
												How accurate is the information
												provided?
											</b>
											<br />
											We rely on official government
											sources for all our data, ensuring a
											high degree of accuracy. However, we
											recommend cross-referencing with the
											original sources for critical
											decisions.
										</li>
										<li>
											<b>
												Can I contribute or report an
												issue?
											</b>
											<br />
											Absolutely! We value feedback from
											our users. If you spot an issue or
											have suggestions, please{' '}
											<a href='mailto:admin@congress.dev'>
												contact us
											</a>{' '}
											to reach out.
										</li>
										<li>
											<b>
												Does Congress.dev provide legal
												advice?
											</b>
											<br />
											No, Congress.dev is an informational
											tool and does not provide legal
											advice. For legal guidance, consult
											a qualified attorney or legal
											expert.
										</li>
										<li>
											<b>
												How can I stay updated about new
												features or updates?
											</b>
											<br />
											You can follow us on{' '}
											<a
												href='https://x.com/congress_dev'
												rel='noopener'
												target='_blank'
											>
												X.com
											</a>{' '}
											for the latest news, updates, and
											feature releases.
										</li>
										<li>
											<b>
												Can I use the data for my own
												projects or research?
											</b>
											<br />
											Yes, all data on Congress.dev is
											sourced from public domain datasets
											and can be freely used under
											applicable laws. Be sure to review
											the terms of use for the original
											data sources as well.
										</li>
									</ol>
								</Paper>
							</Box>
						</Box>
					</Paper>
				</Container>
			</Box>
		</HydrateClient>
	);
}
