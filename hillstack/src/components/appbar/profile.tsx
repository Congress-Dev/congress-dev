import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import {
	Avatar,
	Box,
	IconButton,
	ListItemIcon,
	ListItemText,
	Menu,
	MenuItem,
	Tooltip,
	Typography,
} from '@mui/material';

import { signIn, signOut, useSession } from 'next-auth/react';
import type { MouseEvent } from 'react';
import { useState } from 'react';

export function Profile() {
	const { data: session } = useSession();

	const settings = session
		? [{ title: 'Logout', action: signOut, icon: LogoutIcon }]
		: [
				{
					title: 'Login',
					action: () => {
						signIn('google', {
							redirect: false,
						});
					},
					icon: LoginIcon,
				},
			];

	const [anchorElUser, setAnchorElUser] = useState<null | HTMLElement>(null);

	const handleOpenUserMenu = (event: MouseEvent<HTMLElement>) => {
		setAnchorElUser(event.currentTarget);
	};

	const handleCloseUserMenu = () => {
		setAnchorElUser(null);
	};

	return (
		<Box
			sx={{
				flexGrow: 1,
				display: 'flex',
				justifyContent: 'flex-end',
			}}
		>
			<Tooltip title='Profile'>
				<IconButton onClick={handleOpenUserMenu} sx={{ p: 0 }}>
					{session ? (
						<Avatar
							alt={session.user?.name ?? 'User'}
							src={session.user?.image ?? ''}
						/>
					) : (
						<Avatar />
					)}
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
						key={setting.title}
						onClick={() => {
							setting.action();
							handleCloseUserMenu();
						}}
						sx={{ minWidth: '170px' }}
					>
						<ListItemIcon>
							<setting.icon />
						</ListItemIcon>
						<ListItemText>
							<Typography>{setting.title}</Typography>
						</ListItemText>
					</MenuItem>
				))}
			</Menu>
		</Box>
	);
}
