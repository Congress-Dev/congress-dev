import type { Params } from 'next/dist/server/request/params';
import BillSpendingTable from '~/app/congress/bills/[billId]/spending/table';
import { api } from '~/trpc/server';

export default async function BillSpendingPage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { billId } = await params;

	const data = await api.bill.appropriations({
		id: Number(billId as string),
	});

	return <BillSpendingTable rows={data} />;
}
