import { Box, Card, Toolbar, Typography } from '@mui/material';
import type { Params } from 'next/dist/server/request/params';
// import { useState } from 'react';
import { api } from '~/trpc/server';

const cleanStr = (input: string) =>
	input?.replace(/<usccite\b[^>]*>(.*?)<\/usccite>/gs, '$1');

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
	diffs,
	depth = 0,
}) => {
	// const [collapsed, setCollapsed] = useState(node.isCollapsed);
	const collapsed = false;

	const hasChildren = node.children && node.children.length > 0;
	const isTarget = node.isTarget;
	const isOnPath = node.isOnPath;
	const hasChange = !!diffs[node.usc_content_id];
	const theDiff = diffs[node.usc_content_id];
	const newContent =
		!node.section_display && !node.heading && !node.content_str;
	const hasDiff =
		theDiff?.section_display || theDiff?.heading || theDiff?.content_str;

	// if (!node.heading && !node.content_str) {
	// 	return;
	// }

	// console.log(node, hasChildren);

	return (
		<div style={{}}>
			{/* Row */}
			{!newContent && (
				<div
					// onClick={() => hasChildren && setCollapsed(!collapsed)}
					style={{
						padding: '4px 6px',
						paddingLeft: depth * INDENT,
						background: hasChange
							? 'rgba(255, 0, 0, 0.09)'
							: 'transparent',
						borderLeft: hasChange
							? '3px solid #d90606ff'
							: '3px solid transparent',
						cursor: hasChildren ? 'pointer' : 'default',
						fontFamily: 'monospace',
						fontSize: '14px',
						display: 'flex',
						alignItems: 'center',
					}}
				>
					{hasChildren ? (
						<span style={{ marginRight: 4, userSelect: 'none' }}>
							<ContentDisplay {...node} />
						</span>
					) : (
						<ContentDisplay {...node} />
					)}
				</div>
			)}
			{hasDiff && (
				<div
					style={{
						padding: '4px 6px',
						paddingLeft: depth * INDENT,
						background: hasDiff
							? 'rgba(30, 255, 0, 0.09)'
							: 'transparent',
						borderLeft: hasDiff
							? '3px solid #18d906ff'
							: '3px solid transparent',
						fontFamily: 'monospace',
						fontSize: '14px',
						display: 'flex',
						alignItems: 'center',
						marginTop: 2,
					}}
				>
					<span>
						<ContentDisplay
							{...{
								...theDiff,
								section_display:
									theDiff.section_display ??
									node.section_display,
								heading: theDiff.heading ?? node.heading,
							}}
						/>
					</span>
				</div>
			)}

			{/* Children */}
			{!collapsed && hasChildren && (
				<div style={{ marginTop: 2 }}>
					{node.children.map((child) => (
						<DiffTreeNode
							depth={depth + 1}
							diffs={diffs}
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
export const DiffTree: React.FC<{ tree: TreeNode }> = ({ tree, diffs }) => {
	return (
		<div style={{ padding: '8px 0' }}>
			<DiffTreeNode diffs={diffs} node={tree} />
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

	return data.mergedTree.map((level) => (
		<Box key={level.id} sx={{ mb: 2 }}>
			<Card>
				<Toolbar variant='dense'>
					<Typography sx={{ mr: 1 }} variant='subtitle1'>
						{`U.S.C ${level.metadata.usc_chapter?.short_title} - ${level.metadata.usc_chapter?.long_title}`}
					</Typography>
				</Toolbar>
				<Box sx={{ px: 2 }}>
					<DiffTree diffs={data.diffs} tree={level} />
				</Box>
			</Card>
		</Box>
	));
}
