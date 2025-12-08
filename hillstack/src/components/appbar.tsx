'use client';

import MenuIcon from '@mui/icons-material/Menu';
import AppBar from '@mui/material/AppBar';
// import Avatar from '@mui/material/Avatar';
import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Drawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
// import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import Toolbar from '@mui/material/Toolbar';
// import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
// import type { MouseEvent } from 'react';
import { useMemo, useState } from 'react';
import { navigationLinks } from '~/constants/navigation';

// const settings = ['Profile', 'Account', 'Dashboard', 'Logout'];

function ResponsiveAppBar() {
	const pathname = usePathname();

	const rootPath = useMemo(() => {
		return `/${pathname.split('/')[1]}`;
	}, [pathname]);

	const [navOpen, setNavOpen] = useState(false);

	// const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);

	// const handleOpenUserMenu = (event: MouseEvent<HTMLElement>) => {
	// 	setAnchorElUser(event.currentTarget);
	// };

	// const handleCloseUserMenu = () => {
	// 	setAnchorElUser(null);
	// };

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
							variant='h6'
						>
							Congress.Dev
						</Typography>

						{/* <Box
							sx={{
								flexGrow: 1,
								display: 'flex',
								justifyContent: 'flex-end',
							}}
						>
							<Tooltip title='Open settings'>
								<IconButton
									onClick={handleOpenUserMenu}
									sx={{ p: 0 }}
								>
									<Avatar
										alt='Remy Sharp'
										src='/static/images/avatar/2.jpg'
									/>
								</IconButton>
							</Tooltip>
							<Menu
								anchorEl={anchorElUser}
								anchorOrigin={{
									vertical: 'bottom',
									horizontal: 'right',
								}}
								id='menu-appbar'
								keepMounted
								onClose={handleCloseUserMenu}
								open={Boolean(anchorElUser)}
								transformOrigin={{
									vertical: 'top',
									horizontal: 'right',
								}}
							>
								{settings.map((setting) => (
									<MenuItem
										key={setting}
										onClick={handleCloseUserMenu}
									>
										<Typography
											sx={{ textAlign: 'center' }}
										>
											{setting}
										</Typography>
									</MenuItem>
								))}
							</Menu>
						</Box> */}
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
							variant='h6'
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

					{/* <Typography>Popular Bills</Typography> */}
				</Box>
			</Drawer>
		</>
	);
}
export default ResponsiveAppBar;
