'use client';

import { Loader2, MousePointer2, ZoomIn, ZoomOut, Maximize2, RotateCcw, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WorkspaceToolbarProps {
  workspaceName: string;
  onNameChange: (name: string) => void;
  dirty: boolean;
  saving: boolean;
  onSave: () => void;
  zoom: number;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onZoomFit: () => void;
  onZoomReset: () => void;
}

export function WorkspaceToolbar({
  workspaceName,
  onNameChange,
  dirty,
  saving,
  onSave,
  zoom,
  onZoomIn,
  onZoomOut,
  onZoomFit,
  onZoomReset,
}: WorkspaceToolbarProps) {
  return (
    <>
      {/* Header */}
      <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between min-w-0">
        <div className="flex flex-col gap-2">
          <input
            value={workspaceName}
            onChange={(e) => onNameChange(e.target.value)}
            className="text-2xl font-light text-white bg-transparent border border-white/10 rounded-lg px-3 py-2 w-full max-w-md focus:outline-none focus:border-white/30"
          />
        </div>
        <button
          onClick={onSave}
          disabled={!dirty || saving}
          className={cn(
            'inline-flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition shrink-0',
            dirty
              ? 'bg-white text-black hover:bg-white/90'
              : 'bg-white/10 text-white/40 cursor-not-allowed'
          )}
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          保存
        </button>
      </div>

      {/* Canvas toolbar */}
      <div className="flex items-center justify-between gap-3 px-4 py-3 border-b border-white/10 text-white/60 text-sm">
        <div className="flex items-center gap-3">
          <MousePointer2 className="w-4 h-4" />
          右键添加节点，拖拽布局，点击节点右侧圆点开始连线（Alt/Option + 滚轮缩放）
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onZoomOut}
            className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-white/10 text-white/60 hover:text-white hover:border-white/40 transition"
            title="缩小"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <div className="w-14 text-center text-xs text-white/50">{Math.round(zoom * 100)}%</div>
          <button
            onClick={onZoomIn}
            className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-white/10 text-white/60 hover:text-white hover:border-white/40 transition"
            title="放大"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={onZoomFit}
            className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-white/10 text-white/60 hover:text-white hover:border-white/40 transition"
            title="适配视图"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
          <button
            onClick={onZoomReset}
            className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-white/10 text-white/60 hover:text-white hover:border-white/40 transition"
            title="还原缩放"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>
    </>
  );
}
