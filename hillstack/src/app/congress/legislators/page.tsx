'use client';

import { OmniSearch } from '~/components/search';
import { useOmniSearchQuery } from '~/contexts';
import { api } from '~/trpc/react';
import type { FilterConfigType } from './layout';
import { LegislatorSearchResult } from './result';

export default function LegislatorSearch() {
	const parameters = useOmniSearchQuery<FilterConfigType>();

	const { data, isLoading } = api.legislator.search.useQuery(parameters);

	return (
		<OmniSearch isLoading={isLoading} results={data?.totalResults ?? 0}>
			{data?.members?.map((legislator) => (
				<LegislatorSearchResult
					key={legislator.bioguide_id}
					legislator={legislator}
				/>
			))}
		</OmniSearch>
	);
}
