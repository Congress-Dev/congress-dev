'use client';

import { keepPreviousData } from '@tanstack/react-query';
import type { FilterConfigType } from '~/app/congress/bills/layout';
import { OmniSearch } from '~/components/search';
import { useOmniSearchQuery } from '~/contexts';
import { api } from '~/trpc/react';
import { BillSearchResult } from './result';

export default function BillSearch() {
	const parameters = useOmniSearchQuery<FilterConfigType>();

	const { data, isFetching } = api.bill.search.useQuery(parameters, {
		placeholderData: keepPreviousData,
		retry: 0,
	});

	return (
		<OmniSearch isLoading={isFetching} results={data?.totalResults ?? 0}>
			{data?.legislation?.map((bill) => (
				<BillSearchResult bill={bill} key={bill.legislation_id} />
			))}
		</OmniSearch>
	);
}
