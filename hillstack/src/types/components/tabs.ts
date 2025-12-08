export interface NavigationTab {
	id: number;
	label?: string;
	icon: React.ReactElement;
}

export interface NavigationTabs {
	[key: string]: NavigationTab;
}
