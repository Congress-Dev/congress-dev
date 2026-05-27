'use client';

import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Box, CircularProgress, Typography } from '@mui/material';
import { SimpleTreeView } from '@mui/x-tree-view/SimpleTreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';
import { useParams, useRouter } from 'next/navigation';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '~/trpc/react';

interface SectionNode {
	usc_section_id: number;
	usc_ident: string | null;
	number: string | null;
	section_display: string | null;
	heading: string | null;
	content_type: string | null;
	usc_chapter_id: number | null;
	parent_id: number | null;
}

interface ContentItem {
	usc_content_id: number;
	usc_ident: string | null;
	parent_id: number | null;
	order_number: number | null;
	section_display: string | null;
	heading: string | null;
	content_str: string | null;
	content_type: string | null;
	number: string | null;
	usc_section_id: number | null;
}

interface ContentTreeNode extends ContentItem {
	children: ContentTreeNode[];
}

function buildContentTree(items: ContentItem[]): ContentTreeNode[] {
	const map = new Map<number, ContentTreeNode>();
	const roots: ContentTreeNode[] = [];

	for (const item of items) {
		map.set(item.usc_content_id, { ...item, children: [] });
	}

	for (const item of items) {
		const node = map.get(item.usc_content_id);
		if (!node) continue;
		const parent = item.parent_id ? map.get(item.parent_id) : undefined;
		if (parent) {
			parent.children.push(node);
		} else {
			roots.push(node);
		}
	}

	return roots;
}

function stripCitations(str: string | null): string {
	if (!str) return '';
	return str
		.replace(/<usccite\b[^>]*>(.*?)<\/usccite>/gs, '$1')
		.replace(/\\n/g, ' ');
}

function ContentNode({
	node,
	depth,
}: {
	node: ContentTreeNode;
	depth: number;
}) {
	const hasHeading = node.heading != null && node.heading.trim() !== '';

	return (
		<Box
			sx={{
				ml: depth > 0 ? 2 : 0,
				borderLeft: depth > 0 ? '1px dashed' : 'none',
				borderColor: 'divider',
				pl: depth > 0 ? 1.5 : 0,
				py: 0.25,
			}}
		>
			<Box>
				{hasHeading ? (
					<Typography
						component='span'
						sx={{ fontFamily: 'monospace', fontSize: '13px' }}
						variant='subtitle2'
					>
						<b>
							{node.section_display} {node.heading}
						</b>
					</Typography>
				) : (
					<Typography
						component='span'
						sx={{
							fontFamily: 'monospace',
							fontSize: '13px',
							fontWeight: 'bold',
						}}
					>
						{node.section_display}{' '}
					</Typography>
				)}
				<Typography
					component={hasHeading ? 'div' : 'span'}
					sx={{
						fontFamily: 'monospace',
						fontSize: '13px',
						ml: hasHeading ? 2.5 : 0,
						display: hasHeading ? 'block' : 'inline',
					}}
				>
					{stripCitations(node.content_str)}
				</Typography>
			</Box>
			{node.children
				.sort((a, b) => (a.order_number ?? 0) - (b.order_number ?? 0))
				.map((child) => (
					<ContentNode
						depth={depth + 1}
						key={child.usc_content_id}
						node={child}
					/>
				))}
		</Box>
	);
}

function USCContentView({
	chapterId,
	sectionNumber,
}: {
	chapterId: number;
	sectionNumber: string;
}) {
	const { data, isLoading } = api.uscode.sectionContent.useQuery({
		chapterId,
		sectionNumber,
	});

	if (isLoading) {
		return (
			<Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
				<CircularProgress size={24} />
			</Box>
		);
	}

	if (!data || data.length === 0) {
		return (
			<Typography color='text.secondary' sx={{ py: 2 }}>
				No content found for this section.
			</Typography>
		);
	}

	const tree = buildContentTree(data);

	return (
		<Box sx={{ py: 1 }}>
			{tree.map((node) => (
				<ContentNode depth={0} key={node.usc_content_id} node={node} />
			))}
		</Box>
	);
}

function SidebarTreeNode({
	section,
	releaseId,
	onSelectSection,
	loadedChildren,
	onExpand,
}: {
	section: SectionNode;
	releaseId: string;
	onSelectSection: (shortTitle: string, sectionNumber: string) => void;
	loadedChildren: Map<string, SectionNode[]>;
	onExpand: (chapterId: number, parentId: number) => void;
}) {
	const isLeaf = section.content_type === 'section';
	const nodeId = `section-${section.usc_section_id}`;
	const children = loadedChildren.get(String(section.usc_section_id)) ?? [];
	const prettyDisplay =
		section.content_type === 'section'
			? (section.section_display ?? '').replace(/SS/g, '\u00A7')
			: (section.section_display ?? '');

	return (
		<TreeItem
			itemId={nodeId}
			label={`${prettyDisplay} ${section.heading ?? ''}`}
			onClick={() => {
				if (isLeaf && section.number) {
					onSelectSection(
						String(section.usc_chapter_id),
						section.number,
					);
				} else if (
					!isLeaf &&
					children.length === 0 &&
					section.usc_chapter_id
				) {
					onExpand(section.usc_chapter_id, section.usc_section_id);
				}
			}}
		>
			{!isLeaf &&
				children.map((child) => (
					<SidebarTreeNode
						key={child.usc_section_id}
						loadedChildren={loadedChildren}
						onExpand={onExpand}
						onSelectSection={onSelectSection}
						releaseId={releaseId}
						section={child}
					/>
				))}
			{!isLeaf && children.length === 0 && (
				<TreeItem itemId={`${nodeId}-placeholder`} label='Loading...' />
			)}
		</TreeItem>
	);
}

export default function USCodeViewer() {
	const params = useParams();
	const router = useRouter();
	const releaseId = params.releaseId as string;
	const pathParts = (params.path as string[] | undefined) ?? [];
	const urlTitle = pathParts[0] ?? null;
	const urlSection = pathParts[1] ?? null;

	const [selectedChapterId, setSelectedChapterId] = useState<number | null>(
		null,
	);
	const [selectedSection, setSelectedSection] = useState<string | null>(
		urlSection,
	);
	const [loadedChildren, setLoadedChildren] = useState<
		Map<string, SectionNode[]>
	>(new Map());
	const [expandedItems, setExpandedItems] = useState<string[]>([]);

	const { data: titles, isLoading: titlesLoading } =
		api.uscode.titles.useQuery({
			releaseId: Number(releaseId),
		});

	const titleMap = useMemo(() => {
		const map = new Map<string, number>();
		if (titles) {
			for (const t of titles) {
				if (t.short_title) {
					map.set(t.short_title, t.usc_chapter_id);
				}
			}
		}
		return map;
	}, [titles]);

	useEffect(() => {
		if (urlTitle && titleMap.has(urlTitle)) {
			const chapId = titleMap.get(urlTitle);
			if (chapId == null) return;
			setSelectedChapterId(chapId);
			if (urlSection) {
				setSelectedSection(urlSection);
			}
		}
	}, [urlTitle, urlSection, titleMap]);

	const handleLoadLevels = useCallback(
		async (chapterId: number, parentId: number | null) => {
			const key =
				parentId != null ? String(parentId) : `chapter-${chapterId}`;
			if (loadedChildren.has(key)) return;

			try {
				const result = await fetch(
					`/api/trpc/uscode.levels?input=${encodeURIComponent(
						JSON.stringify({ json: { chapterId, parentId } }),
					)}`,
				);
				const json = await result.json();
				const sections: SectionNode[] = json?.result?.data?.json ?? [];
				setLoadedChildren((prev) => {
					const next = new Map(prev);
					next.set(key, sections);
					return next;
				});
			} catch {
				// silently fail
			}
		},
		[loadedChildren],
	);

	const handleSelectSection = useCallback(
		(chapterIdStr: string, sectionNumber: string) => {
			const chapterId = Number(chapterIdStr);
			setSelectedChapterId(chapterId);
			setSelectedSection(sectionNumber);

			const title = titles?.find((t) => t.usc_chapter_id === chapterId);
			if (title?.short_title) {
				router.push(
					`/congress/uscode/${releaseId}/${title.short_title}/${sectionNumber}`,
				);
			}
		},
		[titles, releaseId, router],
	);

	const handleTitleExpand = useCallback(
		(chapterId: number) => {
			const key = `chapter-${chapterId}`;
			if (!loadedChildren.has(key)) {
				handleLoadLevels(chapterId, null);
			}
		},
		[loadedChildren, handleLoadLevels],
	);

	const handleItemExpansionToggle = useCallback(
		(_event: React.SyntheticEvent | null, itemIds: string[]) => {
			setExpandedItems(itemIds);

			for (const itemId of itemIds) {
				if (itemId.startsWith('title-')) {
					const chapterId = Number(itemId.replace('title-', ''));
					handleTitleExpand(chapterId);
				} else if (itemId.startsWith('section-')) {
					const sectionId = Number(itemId.replace('section-', ''));
					const key = String(sectionId);
					if (!loadedChildren.has(key)) {
						const allSections = Array.from(
							loadedChildren.values(),
						).flat();
						const section = allSections.find(
							(s) => s.usc_section_id === sectionId,
						);
						if (section?.usc_chapter_id) {
							handleLoadLevels(section.usc_chapter_id, sectionId);
						}
					}
				}
			}
		},
		[handleTitleExpand, loadedChildren, handleLoadLevels],
	);

	if (titlesLoading) {
		return (
			<Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
				<CircularProgress />
			</Box>
		);
	}

	return (
		<Box
			sx={{
				display: 'flex',
				gap: 2,
				height: 'calc(100vh - 160px)',
			}}
		>
			<Box
				sx={{
					width: { xs: '100%', md: 320 },
					minWidth: { md: 280 },
					maxWidth: { md: 400 },
					overflow: 'auto',
					borderRight: { md: '1px solid' },
					borderColor: 'divider',
					pr: { md: 1 },
				}}
			>
				<Typography sx={{ mb: 1 }} variant='subtitle2'>
					Titles
				</Typography>
				<SimpleTreeView
					expandedItems={expandedItems}
					onExpandedItemsChange={handleItemExpansionToggle}
					slots={{
						collapseIcon: ExpandMoreIcon,
						expandIcon: ChevronRightIcon,
					}}
				>
					{titles?.map((title) => {
						const titleNodeId = `title-${title.usc_chapter_id}`;
						const children =
							loadedChildren.get(
								`chapter-${title.usc_chapter_id}`,
							) ?? [];

						return (
							<TreeItem
								itemId={titleNodeId}
								key={title.usc_chapter_id}
								label={`${title.short_title} - ${title.long_title ?? ''}`}
							>
								{children.map((section) => (
									<SidebarTreeNode
										key={section.usc_section_id}
										loadedChildren={loadedChildren}
										onExpand={(chapId, parentId) =>
											handleLoadLevels(chapId, parentId)
										}
										onSelectSection={handleSelectSection}
										releaseId={releaseId}
										section={section}
									/>
								))}
								{children.length === 0 && (
									<TreeItem
										itemId={`${titleNodeId}-placeholder`}
										label='Loading...'
									/>
								)}
							</TreeItem>
						);
					})}
				</SimpleTreeView>
			</Box>

			<Box
				sx={{
					flex: 1,
					overflow: 'auto',
					display: {
						xs: selectedSection ? 'block' : 'none',
						md: 'block',
					},
					pl: { md: 1 },
				}}
			>
				{selectedChapterId && selectedSection ? (
					<USCContentView
						chapterId={selectedChapterId}
						sectionNumber={selectedSection}
					/>
				) : (
					<Box
						sx={{
							display: 'flex',
							alignItems: 'center',
							justifyContent: 'center',
							height: '100%',
							color: 'text.secondary',
						}}
					>
						<Typography variant='body1'>
							Select a section from the sidebar to view its
							content.
						</Typography>
					</Box>
				)}
			</Box>
		</Box>
	);
}
