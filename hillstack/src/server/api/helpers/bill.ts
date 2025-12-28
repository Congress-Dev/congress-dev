import type { PrismaClient } from 'generated/prisma/client';

interface TreeNode {
	id: number;
	usc_content_id: number;
	parent_id: number | null;
	content_str: string;
	section_display: string;
	heading: string;
	children: TreeNode[];
	isTarget: boolean;
	isOnPath: boolean;
	diffIds?: number[];
	metadata?: TreeNodeMetadata;
}

interface TreeNodeMetadata {
	usc_chapter: {
		short_title: string | null;
		long_title: string | null;
	} | null;
	usc_section: {
		number: string | null;
		heading: string | null;
	} | null;
}

interface Diff {
	usc_content_id: number;
	section_display: string | null;
	heading: string | null;
	content_str: string | null;
	usc_section: {
		number: string | null;
		heading: string | null;
	} | null;
	usc_content_diff_id: number | null;
	usc_chapter: {
		short_title: string | null;
		long_title: string | null;
	} | null;
}

interface Sibling {
	parent_id: number | null;
	section_display: string | null;
	heading: string | null;
	content_str: string | null;
	usc_content_id: number;
}

/**
 * Fetches the full parent chain for a given USC Content ID.
 * Returns array from root -> leaf (target item).
 */
async function fetchParentChain(
	prisma: PrismaClient,
	uscContentId: number | null,
): Promise<Sibling[]> {
	const chain = [];
	let current: number | null = uscContentId;

	while (current) {
		const node: Sibling | null = await prisma.usc_content.findUnique({
			where: { usc_content_id: current },
			select: {
				usc_content_id: true,
				parent_id: true,
				content_str: true,
				heading: true,
				section_display: true,
			},
		});

		if (!node) break;

		chain.push(node);
		current = node.parent_id;
	}

	return chain.reverse();
}

/**
 * Given a node, fetch all children (direct descendants).
 */
async function fetchChildren(prisma: PrismaClient, parentId: number | null) {
	return prisma.usc_content.findMany({
		where: { parent_id: parentId },
		select: {
			parent_id: true,
			heading: true,
			content_str: true,
			usc_content_id: true,
			section_display: true,
		},
		orderBy: { usc_content_id: 'asc' },
	});
}

/**
 * Slice siblings so only ±3 around the target remain.
 */
function sliceSiblingsAroundTarget(siblings: Sibling[], targetId: number) {
	const idx = siblings.findIndex((s) => s.usc_content_id === targetId);
	if (idx === -1) return siblings;

	const start = Math.max(idx - 3, 0);
	const end = Math.min(idx + 3, siblings.length - 1);

	return siblings.slice(start, end + 1);
}

/**
 * Build a nested structure from the root to the target.
 * Only include siblings within ±3 range at each level.
 */
async function buildNestedTree(
	prisma: PrismaClient,
	chain: any[],
	targetId: number | null,
) {
	let cursor: TreeNode | null = null;
	let rootNode: TreeNode | null = null;

	for (let i = 0; i < chain.length; i++) {
		const node = chain[i];

		let visibleSiblings = [node];

		if (i === chain.length - 1) {
			// Fetch siblings at this parent level
			const siblings = await fetchChildren(prisma, node.parent_id);

			// Only keep ±3 siblings around the current chain node
			visibleSiblings = sliceSiblingsAroundTarget(
				siblings,
				node.usc_content_id,
			);
		}

		const children: TreeNode[] = visibleSiblings.map((sib) => ({
			id: sib.usc_content_id,
			usc_content_id: sib.usc_content_id,
			parent_id: sib.parent_id,
			content_str: sib.content_str,
			section_display: sib.section_display,
			heading: sib.heading,
			children: [],
			isTarget: sib.usc_content_id === targetId,
			isOnPath: sib.usc_content_id === node.usc_content_id,
			isCollapsed: sib.usc_content_id !== node.usc_content_id, // collapse siblings except the one on the path
		}));

		const thisNode = children.find(
			(c) => c.usc_content_id === node.usc_content_id,
		);

		if (thisNode) {
			if (!cursor) {
				// this is the root
				rootNode = thisNode;
				cursor = thisNode;
			} else {
				// attach to previous cursor
				cursor.children = children;
				cursor = thisNode;
			}
		}
	}

	return rootNode;
}

/**
 * Main function: builds a nested "GitHub-like collapsed tree" for each diff.
 */
export async function buildNestedDiffTrees(
	prisma: PrismaClient,
	diffs: Diff[],
) {
	const results = [];

	for (const diff of diffs) {
		const chain = await fetchParentChain(prisma, diff.usc_content_id);
		const tree = await buildNestedTree(prisma, chain, diff.usc_content_id);

		results.push({
			diffId: diff.usc_content_id,
			metadata: {
				usc_chapter: diff.usc_chapter,
				usc_section: diff.usc_section,
			},
			tree,
		});
	}

	return results;
}

/**
 * Merge multiple diff trees (with associated diffId) into one unified tree
 */
export function mergeDiffTrees(
	treesWithDiffId: {
		diffId: number;
		tree: TreeNode | null;
		metadata: TreeNodeMetadata;
	}[],
): TreeNode[] {
	const nodeMap = new Map<number, TreeNode>();

	function mergeNode(
		node: TreeNode | null,
		diffId: number,
		metadata: TreeNodeMetadata,
	) {
		if (!node) {
			return;
		}
		if (nodeMap.has(node.id)) {
			const existing = nodeMap.get(node.id);

			if (!existing) {
				return;
			}

			// Merge children recursively
			node.children.forEach((child) => {
				mergeNodeInto(child, existing.children, diffId);
			});

			// Merge diffIds if this node is a target
			if (node.isTarget) {
				if (!existing.diffIds) existing.diffIds = [];
				if (!existing.diffIds.includes(diffId))
					existing.diffIds.push(diffId);
			}

			// Merge isOnPath
			existing.isOnPath = existing.isOnPath || node.isOnPath;
		} else {
			// Clone node and attach diffId if target
			const copy: TreeNode = {
				...node,
				children: [...node.children],
				diffIds: node.isTarget ? [diffId] : [],
				metadata,
			};
			nodeMap.set(copy.id, copy);
		}
	}

	function mergeNodeInto(
		node: TreeNode,
		children: TreeNode[],
		diffId: number,
	) {
		const existing = children.find((c) => c.id === node.id);
		if (existing) {
			node.children.forEach((child) => {
				mergeNodeInto(child, existing.children, diffId);
			});
			if (node.isTarget) {
				if (!existing.diffIds) existing.diffIds = [];
				if (!existing.diffIds.includes(diffId))
					existing.diffIds.push(diffId);
			}
			existing.isOnPath = existing.isOnPath || node.isOnPath;
		} else {
			children.push({
				...node,
				children: [...node.children],
				diffIds: node.isTarget ? [diffId] : [],
			});
		}
	}

	// Merge all trees
	for (const { diffId, tree, metadata } of treesWithDiffId) {
		mergeNode(tree, diffId, metadata);
	}

	// Return top-level roots (parent_id === null)
	return Array.from(nodeMap.values()).filter((n) => n.parent_id === null);
}
