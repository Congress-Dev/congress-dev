import { Box, Card, Toolbar, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
// import { useState } from 'react';
import { api } from '~/trpc/server';

const cleanStr = (input: string) =>
	input.replace(/<usccite\b[^>]*>(.*?)<\/usccite>/gs, '$1');

export interface TreeNode {
	id: number;
	content: string;
	children: TreeNode[];
	isTarget: boolean;
	isOnPath: boolean;
	isCollapsed: boolean;
}

interface NodeProps {
	node: TreeNode;
	depth?: number;
}

const INDENT = 18;

export const ContentDisplay = (content) => {
	return (
		<Box>
			<Box sx={{ display: 'flex' }}>
				<Typography
					sx={{ mr: 0.5, fontFamily: 'monospace' }}
					variant={'subtitle2'}
				>
					{content.section_display}
				</Typography>
				<Typography sx={{ flex: 1, fontFamily: 'monospace' }}>
					{content.heading ?? cleanStr(content.content_str)}
				</Typography>
			</Box>
			{content.heading && (
				<Typography sx={{ ml: 3, fontFamily: 'monospace' }}>
					{cleanStr(content.content_str)}
				</Typography>
			)}
		</Box>
	);
};

export const DiffTreeNode: React.FC<NodeProps> = ({
	node,
	diff,
	depth = 0,
}) => {
	// const [collapsed, setCollapsed] = useState(node.isCollapsed);
	const collapsed = false;

	const hasChildren = node.children && node.children.length > 0;
	const isTarget = node.isTarget;
	const isOnPath = node.isOnPath;

	if (!node.heading && !node.content_str) {
		return;
	}

	// console.log(node, hasChildren);

	return (
		<div style={{ marginLeft: depth * INDENT }}>
			{/* Row */}
			<div
				// onClick={() => hasChildren && setCollapsed(!collapsed)}
				style={{
					padding: '4px 6px',
					background: isTarget
						? 'rgba(255, 200, 0, 0.25)'
						: isOnPath
							? 'rgba(0, 120, 255, 0.12)'
							: 'transparent',
					borderLeft: isTarget
						? '3px solid #d97706'
						: '3px solid transparent',
					cursor: hasChildren ? 'pointer' : 'default',
					fontFamily: 'monospace',
					fontSize: '14px',
					display: 'flex',
					alignItems: 'center',
				}}
			>
				{/* ▾ / ▸ arrow */}
				{hasChildren ? (
					<span style={{ marginRight: 4, userSelect: 'none' }}>
						<ContentDisplay {...node} />
					</span>
				) : (
					<ContentDisplay {...node} />
				)}

				{/* Content */}
			</div>
			<div
				// onClick={() => hasChildren && setCollapsed(!collapsed)}
				style={{
					padding: '4px 6px',
					background: isTarget
						? 'rgba(30, 255, 0, 0.25)'
						: isOnPath
							? 'rgba(0, 120, 255, 0.12)'
							: 'transparent',
					borderLeft: isTarget
						? '3px solid #18d906ff'
						: '3px solid transparent',
					cursor: hasChildren ? 'pointer' : 'default',
					fontFamily: 'monospace',
					fontSize: '14px',
					display: isTarget ? 'flex' : 'none',
					alignItems: 'center',
					marginTop: 2,
				}}
			>
				{/* Content */}
				<span>
					<ContentDisplay {...{ ...node, content_str: diff }} />
				</span>
			</div>

			{/* Children */}
			{!collapsed && hasChildren && (
				<div style={{ marginTop: 2 }}>
					{node.children.map((child) => (
						<DiffTreeNode
							depth={depth + 1}
							diff={diff}
							key={child.id}
							node={child}
						/>
					))}
				</div>
			)}
		</div>
	);
};

/**
 * Tree renderer root
 */
export const DiffTree: React.FC<{ tree: TreeNode }> = ({ tree, diff }) => {
	return (
		<div style={{ padding: '8px 0' }}>
			<DiffTreeNode diff={diff} node={tree} />
		</div>
	);
};

export default async function BillChangesPage({
	params,
}: {
	params: Promise<Params>;
}) {
	const { billId } = await params;

	const data = await api.bill.diffs({
		id: Number(billId as string),
	});

	console.log(data);

	return data.map((level) => (
		<Box key={level.diffId} sx={{ mb: 2 }}>
			<Card>
				<Toolbar
					sx={{
						py: 1,
						display: 'flex',
						flexDirection: 'column',
						alignItems: 'flex-start',
					}}
					variant='dense'
				>
					<Typography sx={{ mr: 1 }} variant='subtitle1'>
						{`${level.usc_chapter?.short_title} - ${level.usc_chapter?.long_title}`}
					</Typography>
					<Typography variant='subtitle2'>
						{`§ ${level.usc_section.number}. ${level.usc_section.heading}`}
					</Typography>
				</Toolbar>
				<DiffTree diff={level.diffStr} tree={level.tree} />
			</Card>
		</Box>
	));
	// console.log(data);

	// return (
	// 	<Box>
	// 		{data.map((usc_chapter) => {
	// 			const usc_section = usc_chapter.children[0];

	// 			return (
	// 				<Box key={usc_chapter.usc_chapter_id}>
	// 					<Toolbar
	// 						sx={{
	// 							py: 1,
	// 							display: 'flex',
	// 							flexDirection: 'column',
	// 							alignItems: 'flex-start',
	// 						}}
	// 						variant='dense'
	// 					>
	// 						<Typography sx={{ mr: 1 }} variant='subtitle1'>
	// 							{`${usc_chapter?.short_title} - ${usc_chapter?.long_title}`}
	// 						</Typography>
	// 						<Typography variant='subtitle2'>
	// 							{`§ ${usc_section.number}. ${usc_section.heading}`}
	// 						</Typography>
	// 					</Toolbar>
	// 				</Box>
	// 			);
	// 		})}
	// 	</Box>
	// );

	// return null;
	// <Box>
	// 	{/* {data.diffs.map((diff) => (
	// 		<Card key={diff.usc_content_diff_id} sx={{ mb: 2 }}>
	// 			<Toolbar variant='dense'>
	// 				{diff.usc_chapter?.short_title}{' '}
	// 				{diff.usc_chapter?.long_title}
	// 			</Toolbar>
	// 			<Box sx={{ p: 1 }}>
	// 				<Typography color='error'>
	// 					{diff.usc_content?.content_str?.replace(
	// 						/<usccite\b[^>]*>(.*?)<\/usccite>/gs,
	// 						'$1',
	// 					)}
	// 				</Typography>
	// 				<Typography color='success'>
	// 					{diff.content_str?.replace(
	// 						/<usccite\b[^>]*>(.*?)<\/usccite>/gs,
	// 						'$1',
	// 					)}
	// 				</Typography>
	// 			</Box>
	// 		</Card>
	// 	))} */}
	// 	{Object.keys(data.extras).map((extraKey) => {
	// 		const extra = data.extras[extraKey as keyof typeof data.extras];
	// 		const diffByContentId = extra.diff.reduce((acc, diff) => {
	// 			acc[diff.usc_content.usc_content_id] = diff;
	// 			return acc;
	// 		}, {});
	// 		const { usc_chapter, usc_section } = extra.diff[0];
	// 		return (
	// 			<Card key={extraKey} sx={{ mb: 2 }}>
	// 				<Toolbar
	// 					sx={{
	// 						py: 1,
	// 						display: 'flex',
	// 						flexDirection: 'column',
	// 						alignItems: 'flex-start',
	// 					}}
	// 					variant='dense'
	// 				>
	// 					<Typography sx={{ mr: 1 }} variant='subtitle1'>
	// 						{`${usc_chapter?.short_title} - ${usc_chapter?.long_title}`}
	// 					</Typography>
	// 					<Typography variant='subtitle2'>
	// 						{`§ ${usc_section.number}. ${usc_section.heading}`}
	// 					</Typography>
	// 				</Toolbar>
	// 				<Box sx={{ p: 1 }}>
	// 					<Typography
	// 						sx={{ fontFamily: 'monospace', ml: 3, mb: 1 }}
	// 					>
	// 						{`${extra.parent.heading} ${extra.parent.content_str}`}
	// 					</Typography>
	// 					{extra.sections.map((section) => {
	// 						return (
	// 							<Box key={section.usc_content_id}>
	// 								<Box sx={{ mb: 1, ml: 6 }}>
	// 									{diffByContentId[
	// 										section.usc_content_id
	// 									] ? (
	// 										<>
	// 											<Typography
	// 												color='error'
	// 												sx={{
	// 													fontFamily:
	// 														'monospace',
	// 													backgroundColor:
	// 														'rgba(255,0,0,0.1)',
	// 												}}
	// 											>
	// 												{cleanStr(
	// 													section.content_str,
	// 												)}
	// 											</Typography>
	// 											<Typography
	// 												color='success'
	// 												sx={{
	// 													fontFamily:
	// 														'monospace',
	// 													backgroundColor:
	// 														'rgba(0,255,0,0.05)',
	// 												}}
	// 											>
	// 												{cleanStr(
	// 													diffByContentId[
	// 														section
	// 															.usc_content_id
	// 													].content_str,
	// 												)}
	// 											</Typography>
	// 										</>
	// 									) : (
	// 										<Typography
	// 											sx={{
	// 												fontFamily: 'monospace',
	// 											}}
	// 										>
	// 											{cleanStr(
	// 												section.content_str,
	// 											)}
	// 										</Typography>
	// 									)}
	// 								</Box>
	// 							</Box>
	// 						);
	// 					})}
	// 					{/* <Typography color='error'>
	// 					{diff.usc_content?.content_str?.replace(
	// 						/<usccite\b[^>]*>(.*?)<\/usccite>/gs,
	// 						'$1',
	// 					)}
	// 				</Typography>
	// 				<Typography color='success'>
	// 					{diff.content_str?.replace(
	// 						/<usccite\b[^>]*>(.*?)<\/usccite>/gs,
	// 						'$1',
	// 					)}
	// 				</Typography> */}
	// 				</Box>
	// 			</Card>
	// 		);
	// 	})}
	// </Box>
	// );
}
