'use client';
import MenuIcon from '@mui/icons-material/Menu';

import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import MenuItem from '@mui/material/MenuItem';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

import { useMemo, useState } from 'react';
import { Profile } from '~/components/appbar/profile';
import { navigationLinks } from '~/constants/navigation';

function ResponsiveAppBar() {
	const pathname = usePathname();

	const rootPath = useMemo(() => {
		return `/${pathname.split('/')[1]}`;
	}, [pathname]);

	const [navOpen, setNavOpen] = useState(false);

	return (
		<>
			<AppBar position='static'>
				<Box sx={{ px: 2 }}>
					<Toolbar disableGutters>
						<Box
							sx={{
								display: 'flex',
								mr: 2,
							}}
						>
							<IconButton
								color='inherit'
								onClick={() => setNavOpen(true)}
								size='small'
							>
								<MenuIcon />
							</IconButton>
						</Box>

						<Box sx={{ mr: 1 }}>
							<Image
								alt='logo'
								height={32}
								src={'/logo.png'}
								width={32}
							/>
						</Box>
						<Typography
							noWrap
							sx={{
								mr: 2,
								fontWeight: 300,
								color: 'inherit',
								textDecoration: 'none',
							}}
							variant='h4'
						>
							Congress.Dev
						</Typography>

						<Profile />
					</Toolbar>
				</Box>
			</AppBar>
			<Drawer onClose={() => setNavOpen(false)} open={navOpen}>
				<Box sx={{ px: 2, py: 1 }}>
					<Box
						sx={{
							display: 'flex',
							alignItems: 'center',
							pb: 1,
						}}
					>
						<Box sx={{ mr: 1 }}>
							<Image
								alt='logo'
								height={32}
								src={'/logo.png'}
								width={32}
							/>
						</Box>
						<Typography
							noWrap
							sx={{
								mr: 2,
								fontWeight: 300,
								color: 'inherit',
								textDecoration: 'none',
							}}
							variant='h4'
						>
							Congress.Dev
						</Typography>
					</Box>
					<Divider sx={{ mb: 1 }} />

					{navigationLinks.map((page) => (
						<MenuItem
							key={page.label}
							selected={rootPath === page.href}
							sx={{
								minWidth: '300px',
								pl: 1,
								mb: 1,
								borderRadius: 1,
							}}
						>
							<Link
								href={page.href}
								onClick={() => setNavOpen(false)}
								style={{ width: '100%' }}
							>
								<Box
									sx={{
										display: 'flex',
										alignItems: 'center',
									}}
								>
									<page.icon
										fontSize='small'
										sx={{
											mr: 1,
										}}
									/>
									<Typography>{page.label}</Typography>
								</Box>
							</Link>
						</MenuItem>
					))}

					<Divider sx={{}} />
				</Box>
			</Drawer>
		</>
	);
}
export default ResponsiveAppBar;
