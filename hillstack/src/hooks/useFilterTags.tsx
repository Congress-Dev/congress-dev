import { useCallback, useMemo, useState } from 'react';
import { ToolbarFilter } from '~/components/toolbar';
import type {
	ToolbarFilterConfig,
	ToolbarFilterOption,
	ToolbarFilterOptionMap,
	ToolbarFilterSelections,
} from '~/types/components';

export function useFilterTags<T extends ToolbarFilterOptionMap>(
	config: ToolbarFilterConfig<T>,
) {
	const [tags, setTags] = useState<ToolbarFilterSelections<T>>({});

	const onTagChange = useCallback(
		(tag: string, value: ToolbarFilterOption<keyof T>[] | undefined) => {
			setTags({ ...tags, [tag]: value });
		},
		[tags],
	);

	const removeTag = useCallback(
		(tag: string, selection: ToolbarFilterOption<keyof T>['value']) => {
			const newValue =
				tags[tag]?.filter((val) => val.value !== selection) ?? [];
			setTags({ ...tags, [tag]: newValue.length ? newValue : undefined });
		},
		[tags],
	);

	const filters = useMemo(() => {
		return Object.keys(config).map(
			(key) =>
				config[key] != null && (
					<ToolbarFilter
						key={key}
						multiSelect={config[key].multiSelect}
						onTagChange={onTagChange}
						options={
							config[key].options as ToolbarFilterOption<
								keyof T
							>[]
						}
						prop={key}
						searchable={config[key].searchable}
						title={config[key].title}
						value={tags[key]}
					/>
				),
		);
	}, [tags, config, onTagChange]);

	return { filters, tags, removeTag };
}
