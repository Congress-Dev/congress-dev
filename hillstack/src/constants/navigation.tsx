import AccountBalanceOutlinedIcon from '@mui/icons-material/AccountBalanceOutlined';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import ChevronLeftOutlinedIcon from '@mui/icons-material/ChevronLeftOutlined';
import Diversity2Icon from '@mui/icons-material/Diversity2';
import GavelIcon from '@mui/icons-material/Gavel';
import HistoryEduIcon from '@mui/icons-material/HistoryEdu';
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import LocalPoliceIcon from '@mui/icons-material/LocalPolice';
import SchoolOutlinedIcon from '@mui/icons-material/SchoolOutlined';
import type { NavigationTabs } from '~/types/components';

export const navigationLinks = [
	{ label: 'Home', icon: HomeOutlinedIcon, href: '/' },
	{ label: 'Learn', icon: SchoolOutlinedIcon, href: '/learn' },
	{ label: 'Congress', icon: AccountBalanceOutlinedIcon, href: '/congress' },
	{ label: 'About Us', icon: InfoOutlinedIcon, href: '/about' },
];

export const congressTabs: NavigationTabs = {
	'/': {
		id: 0,
		icon: <ChevronLeftOutlinedIcon />,
		label: '',
	},
	'/congress/bills': {
		id: 1,
		icon: <HistoryEduIcon />,
		label: 'Bills',
	},
	'/congress/uscode': {
		id: 2,
		icon: <LocalPoliceIcon />,
		label: 'U.S. Code',
	},
	'/congress/legislators': {
		id: 3,
		icon: <GavelIcon />,
		label: 'Legislators',
	},
	'/congress/committees': {
		id: 4,
		icon: <Diversity2Icon />,
		label: 'Committees',
	},
	'/congress/insights': {
		id: 5,
		icon: <AutoGraphIcon />,
		label: 'Insights',
	},
};

import DifferenceIcon from '@mui/icons-material/Difference';
import LocalAtmIcon from '@mui/icons-material/LocalAtm';
import ManageSearchIcon from '@mui/icons-material/ManageSearch';
import SmartButtonIcon from '@mui/icons-material/SmartButton';
import type { Params } from 'next/dist/server/request/params';

export const congressBillTabs = ({
	params,
}: {
	params: Params;
}): NavigationTabs => {
	return {
		[`/congress/bills/${params.billId}/overview`]: {
			id: 0,
			icon: <SmartButtonIcon />,
			label: 'Overview',
		},
		[`/congress/bills/${params.billId}/text`]: {
			id: 1,
			icon: <ManageSearchIcon />,
			label: 'Text',
		},
		[`/congress/bills/${params.billId}/changes`]: {
			id: 2,
			icon: <DifferenceIcon />,
			label: 'Changes',
		},
		[`/congress/bills/${params.billId}/spending`]: {
			id: 3,
			icon: <LocalAtmIcon />,
			label: 'Spending',
		},
	};
};
