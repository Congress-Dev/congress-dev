// biome-ignore lint:suspicious/noExplicitAny
export type ToolbarFilterOptionMap = Record<string, any>;

export interface ToolbarFilterOption<T> {
	label: string;
	value: T;
}

export type ToolbarFilterSelections<T extends ToolbarFilterOptionMap> = {
	[K in keyof T]?: ToolbarFilterOption<K>[] | undefined;
};

export type ToolbarFilterOptions<T extends ToolbarFilterOptionMap> =
	| ToolbarFilterOption<T>[]
	| undefined;

export type ToolbarFilterConfig<T extends ToolbarFilterOptionMap> = {
	[K in keyof T]: {
		title: string;
		options: ToolbarFilterOptions<T[K]>;
		multiSelect: boolean;
	};
};
