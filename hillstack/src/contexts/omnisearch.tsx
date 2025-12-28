import React, {
	createContext,
	type Dispatch,
	type SetStateAction,
	useContext,
	useMemo,
	useState,
} from 'react';
import { useFilterTags } from '~/hooks';
import type {
	ToolbarFilterConfig,
	ToolbarFilterOptionMap,
	ToolbarFilterSelections,
} from '~/types/components';
import { useDebounce } from '~/utils';

type OmniSearchQueryTagsType<TConfig extends ToolbarFilterOptionMap> = {
	[K in keyof TConfig]?: TConfig[K]['multiSelect'] extends true
		? TConfig[K]['options'][number]['value'][]
		: TConfig[K]['options'][number]['value'][];
};

type OmniSearchContextType<T extends ToolbarFilterOptionMap> = {
	page: number;
	setPage: Dispatch<SetStateAction<number>>;
	pageSize: number;
	setPageSize: Dispatch<SetStateAction<number>>;
	query: string;
	debouncedQuery: string;
	setQuery: Dispatch<SetStateAction<string>>;
	filters: React.ReactNode;
	tags: ToolbarFilterSelections<T>;
	removeTag: (tag: string, selection: string) => void;
} | null;

export function OmniSearchContextFactory<T extends ToolbarFilterOptionMap>() {
	return createContext<OmniSearchContextType<T>>(null);
}

const OmniSearchContext = OmniSearchContextFactory();

export function OmniSearchProvider<T extends ToolbarFilterOptionMap>({
	filterConfig,
	children,
}: {
	filterConfig: ToolbarFilterConfig<T>;
	children: React.ReactNode;
}) {
	const [page, setPage] = useState(1);
	const [pageSize, setPageSize] = useState(10);
	const [query, setQuery] = useState('');
	const debouncedQuery = useDebounce<string>(query, 500);
	const { filters, tags, removeTag } = useFilterTags(filterConfig);

	const config = useMemo(
		() => ({
			query,
			tags,
			page,
			pageSize,
		}),
		[query, tags, page, pageSize],
	);

	const contextValue = {
		page,
		setPage,
		pageSize,
		setPageSize,
		query,
		debouncedQuery,
		setQuery,
		filters,
		tags,
		removeTag,
		config,
	};

	return (
		<OmniSearchContext.Provider value={contextValue}>
			{children}
		</OmniSearchContext.Provider>
	);
}

export function useOmniSearchContext() {
	const context = useContext(OmniSearchContext);
	if (!context) {
		throw new Error(
			'useOmniSearchContext can only be used inside OmniSearchProvider',
		);
	}
	return context;
}

export function useOmniSearchQuery<A extends ToolbarFilterOptionMap>() {
	// @ts-expect-error
	const context = useContext<OmniSearchContextType<A>>(OmniSearchContext);
	if (!context) {
		throw new Error(
			'useOmniSearchContext can only be used inside OmniSearchProvider',
		);
	}

	const tags: OmniSearchQueryTagsType<A> = Object.keys(context.tags).reduce(
		(acc, tag) => {
			if (context.tags[tag]) {
				// @ts-expect-error
				acc[tag] = Array.isArray(context.tags[tag])
					? context.tags[tag].map((t) => t.value)
					: // @ts-expect-error
						context.tags[tag].value;
			}
			return acc;
		},
		{},
	);

	return {
		query: context.debouncedQuery,
		page: context.page,
		pageSize: context.pageSize,
		...tags,
	};
}
