'use client';

import { keepPreviousData } from '@tanstack/react-query';
import { OmniSearch } from '~/components/search';
import { useOmniSearchQuery } from '~/contexts';
import { api } from '~/trpc/react';
import type { FilterConfigType } from './layout';
import { CommitteeSearchResult } from './result';

export default function CommitteeSearch() {
	const parameters = useOmniSearchQuery<FilterConfigType>();

	const { data, isFetching } = api.committee.search.useQuery(parameters, {
		placeholderData: keepPreviousData,
	});

	return (
		<OmniSearch isLoading={isFetching} results={data?.totalResults ?? 0}>
			{data?.committees?.map((committee) => (
				<CommitteeSearchResult
					committee={committee}
					key={committee.legislation_committee_id}
				/>
			))}
		</OmniSearch>
	);
}
