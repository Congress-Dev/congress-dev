import { useCallback, useMemo, useState } from "react";
import { ToolbarSort } from "~/components/toolbar";
import type {
    ToolbarSortConfig,
    ToolbarFilterOption,
    ToolbarFilterOptionMap,
    ToolbarFilterSelections,
} from "~/types/components";

export function useFilterSort<T extends string>(
    config: ToolbarSortConfig<T> | undefined,
) {
    const [sort, setSort] = useState<string>('');

    const onSortChange = useCallback(
        (tag: string, value: ToolbarFilterOption<keyof T>[] | undefined) => {
            // setSort({ ...sort, [tag]: value });
        },
        [sort],
    );

    const removeSort = useCallback(
        (tag: string, selection: ToolbarFilterOption<keyof T>["value"]) => {
            // const newValue =
            //     sort[tag]?.filter((val) => val.value !== selection) ?? [];
            // setSort({ ...sort, [tag]: newValue.length ? newValue : undefined });
        },
        [sort],
    );

    const sorter = config ? (
        <ToolbarSort options={config.options} value={undefined} title="" prop="" />
    ) : <></>;
    return { sorter, sort, removeSort };
}
