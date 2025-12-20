'use client';

import { useMemo } from 'react';
import type { WorkspaceNode, WorkspaceEdge } from '@/types';
import { NODE_WIDTH, HANDLE_OFFSET_Y } from './types';

interface WorkspaceEdgesProps {
  nodes: WorkspaceNode[];
  edges: WorkspaceEdge[];
  connectingFrom: string | null;
  cursorPos: { x: number; y: number } | null;
}

export function WorkspaceEdges({
  nodes,
  edges,
  connectingFrom,
  cursorPos,
}: WorkspaceEdgesProps) {
  const edgePaths = useMemo(() => {
    return edges
      .map((edge) => {
        const fromNode = nodes.find((node) => node.id === edge.from);
        const toNode = nodes.find((node) => node.id === edge.to);
        if (!fromNode || !toNode) return null;
        const x1 = fromNode.position.x + NODE_WIDTH;
        const y1 = fromNode.position.y + HANDLE_OFFSET_Y;
        const x2 = toNode.position.x;
        const y2 = toNode.position.y + HANDLE_OFFSET_Y;
        const dx = Math.max(80, Math.abs(x2 - x1) * 0.5);
        return {
          id: edge.id,
          d: `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`,
        };
      })
      .filter(Boolean) as Array<{ id: string; d: string }>;
  }, [edges, nodes]);

  const previewPath = useMemo(() => {
    if (!connectingFrom || !cursorPos) return null;
    const fromNode = nodes.find((node) => node.id === connectingFrom);
    if (!fromNode) return null;
    const x1 = fromNode.position.x + NODE_WIDTH;
    const y1 = fromNode.position.y + HANDLE_OFFSET_Y;
    const x2 = cursorPos.x;
    const y2 = cursorPos.y;
    const dx = Math.max(80, Math.abs(x2 - x1) * 0.5);
    return `M ${x1} ${y1} C ${x1 + dx} ${y1}, ${x2 - dx} ${y2}, ${x2} ${y2}`;
  }, [connectingFrom, cursorPos, nodes]);

  return (
    <svg className="absolute inset-0 w-full h-full pointer-events-none">
      {edgePaths.map((edge) => (
        <path
          key={edge.id}
          d={edge.d}
          stroke="rgba(255,255,255,0.4)"
          strokeWidth="2"
          fill="none"
        />
      ))}
      {previewPath && (
        <path
          d={previewPath}
          stroke="rgba(255,255,255,0.25)"
          strokeWidth="2"
          fill="none"
          strokeDasharray="6 6"
        />
      )}
    </svg>
  );
}
