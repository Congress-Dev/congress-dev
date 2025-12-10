import { createTheme } from '@mui/material/styles';

declare module '@mui/material/styles' {
	interface PaletteBrandColorOptions {
		accentDark: string;
		accent: string;
		accentLight: string;
	}

	interface Palette {
		brand: PaletteBrandColorOptions;
	}

	interface PaletteOptions {
		brand: PaletteBrandColorOptions;
	}
}

const darkMode = createTheme({
	typography: {
		fontSize: 14,
		fontFamily: ['Nunito Sans', 'sans-serif'].join(','),
		h1: {
			fontSize: 28,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		h2: {
			fontSize: 21,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		h3: {
			fontSize: 19,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		h4: {
			fontSize: 17,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		h5: {
			fontSize: 15,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		h6: {
			fontSize: 13,
			fontWeight: 'bold',
			lineHeight: 1,
		},
		body1: {
			fontSize: 14,
		},
		body2: {
			fontSize: 14,
		},
		subtitle1: {
			fontSize: 14,
			fontWeight: 'normal',
			display: 'inline-block',
		},
		subtitle2: {
			fontSize: 14,
			display: 'inline',
			fontWeight: 'bold',
			color: '#8f99a8',
		},
		button: {
			fontSize: 14,
		},
		caption: {
			fontSize: 12,
			color: '#8f99a8',
		},
		overline: {
			fontSize: 13,
			fontWeight: 'bold',
			color: '#8f99a8',
			textTransform: 'initial',
			lineHeight: 1,
		},
	},
	palette: {
		mode: 'dark',

		primary: {
			main: '#90CAF9',
			light: '#E3F2FD',
			dark: '#42A5F5',
			contrastText: '#000000',
		},

		secondary: {
			main: '#dadadaff',
			light: '#f3f3f3ff',
			dark: '#c5c5c5ff',
			contrastText: '#000000',
		},

		error: {
			main: '#F44336',
			light: '#E57373',
			dark: '#D32F2F',
			contrastText: '#FFFFFF',
		},

		warning: {
			main: '#FFA726',
			light: '#FFB74D',
			dark: '#F57C00',
			contrastText: '#000000',
		},

		info: {
			main: '#29B6F6',
			light: '#4FC3F7',
			dark: '#0288D1',
			contrastText: '#000000',
		},

		success: {
			main: '#66BB6A',
			light: '#81C784',
			dark: '#388E3C',
			contrastText: '#000000',
		},

		background: {
			default: '#0f1214ff',
			paper: '#0f1214ff',
		},

		brand: {
			accentDark: '#131b22',
			accent: '#253644',
			accentLight: '#7591a8ff',
		},

		text: {
			primary: '#FFFFFFDE', // rgba(255,255,255,0.87)
			secondary: '#FFFFFF99', // rgba(255,255,255,0.60)
			disabled: '#FFFFFF61', // rgba(255,255,255,0.38)
		},

		divider: '#FFFFFF1F', // rgba(255,255,255,0.12)

		action: {
			active: '#FFFFFFDE',
			hover: '#FFFFFF14', // 0.08
			selected: '#FFFFFF29', // 0.16
			disabled: '#FFFFFF61',
			disabledBackground: '#FFFFFF1F',
			focus: '#FFFFFF1F',
		},
	},
});

export const theme = createTheme(darkMode, {
	typography: {
		fontFamily: [
			'Nunito Sans', // Your custom font
			'sans-serif', // Fallback font
		].join(','),
	},
	components: {
		MuiAppBar: {
			styleOverrides: {
				root: {
					borderWidth: '0px',
					borderBottomWidth: '1px',
					backgroundColor: `${darkMode.palette.brand.accentDark} !important`,
					backgroundImage: 'none',
				},
			},
		},
		MuiToolbar: {
			styleOverrides: {
				root: {
					backgroundColor: darkMode.palette.brand.accentDark,
				},
				regular: {
					minHeight: '50px !important',
				},
				dense: {
					padding: '0px 10px',
					borderBottomColor: darkMode.palette.divider,
					borderBottomWidth: '1px',
					borderBottomStyle: 'solid',
				},
			},
		},
		MuiAvatar: {
			styleOverrides: {
				circular: {
					width: '30px',
					height: '30px',
				},
			},
		},
		MuiTab: {
			styleOverrides: {
				root: {
					textTransform: 'none',
					minHeight: '40px',
					padding: '12px 24px',
				},
			},
		},
		MuiPaper: {
			styleOverrides: {
				root: {
					borderWidth: '1px',
					borderColor: darkMode.palette.divider,
					borderStyle: 'solid',
				},
			},
		},
		MuiDrawer: {
			styleOverrides: {
				paper: {
					backgroundColor: `${darkMode.palette.brand.accentDark} !important`,
					backgroundImage: 'none',
				},
			},
		},
		MuiButton: {
			styleOverrides: {
				root: {
					textTransform: 'none',
				},
			},
		},
	},
});
