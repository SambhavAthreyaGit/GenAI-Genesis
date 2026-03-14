"use client";

import { useState } from "react";
import KiCanvasEmbed from "./KiCanvasEmbed";
import ViewerControls from "./ViewerControls";
import ERCStatus from "./ERCStatus";
import type { ProjectData } from "@/lib/types";

interface ViewerPaneProps {
  projectData: ProjectData | null;
  activeView: "schematic" | "pcb";
  onViewChange: (view: "schematic" | "pcb") => void;
  isGenerating?: boolean;
}

export default function ViewerPane({
  projectData,
  activeView,
  onViewChange,
  isGenerating = false,
}: ViewerPaneProps) {
  const currentUrl =
    activeView === "schematic"
      ? projectData?.schematicUrl
      : projectData?.pcbUrl;

  return (
    <section className="flex-1 relative bg-[#030303] overflow-hidden">
      {/* Subtle Grid Background */}
      <div
        className="absolute inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(#ffffff 1px, transparent 1px)",
          backgroundSize: "32px 32px",
        }}
      />

      {/* Main Content Area */}
      <div className="absolute inset-0 flex items-center justify-center p-4">
        {isGenerating ? (
          <GeneratingState />
        ) : projectData ? (
          <div className="relative w-full h-full flex items-center justify-center">
            {/* Canvas Container - constrained size */}
            <div 
              className="relative bg-[#0a0a0a] rounded-xl overflow-hidden border border-white/5 shadow-2xl"
              style={{
                width: "min(calc(100% - 200px), 900px)",
                height: "min(calc(100% - 100px), 600px)",
              }}
            >
              <KiCanvasEmbed 
                src={currentUrl || ""} 
                key={currentUrl}
              />
            </div>
          </div>
        ) : (
          <EmptyState />
        )}
      </div>

      {/* Overlays */}
      {projectData && !isGenerating && (
        <>
          <ERCStatus ercResult={projectData.ercResult} />
          <ViewerControls
            activeView={activeView}
            onViewChange={onViewChange}
            projectName={projectData.projectId}
          />
        </>
      )}

      {/* Generating Indicator */}
      {isGenerating && (
        <div className="absolute top-4 left-4 flex items-center gap-3 glass-panel px-4 py-2 rounded-full border border-primary/20 shadow-xl z-20">
          <div className="relative flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-primary animate-ping absolute" />
            <div className="w-2 h-2 rounded-full bg-primary relative" />
          </div>
          <span className="text-xs font-medium text-on-surface/90">
            Generating...
          </span>
        </div>
      )}
    </section>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-sm px-4">
      <div className="w-16 h-16 rounded-2xl bg-primary/5 border border-primary/10 flex items-center justify-center mb-5">
        <span
          className="material-symbols-outlined text-primary/40 text-3xl"
          style={{ fontVariationSettings: "'FILL' 0, 'wght' 200" }}
        >
          developer_board
        </span>
      </div>
      <h2 className="text-lg font-light text-on-surface/80 mb-2">
        No Design Yet
      </h2>
      <p className="text-on-surface-variant/50 text-xs leading-relaxed">
        Describe your circuit in the chat panel
      </p>
      <div className="mt-5 flex flex-wrap gap-1.5 justify-center">
        {["LED Circuit", "5V Regulator", "555 Timer"].map((example) => (
          <span
            key={example}
            className="px-2.5 py-1 rounded-full bg-white/[0.02] border border-white/5 text-[10px] text-on-surface-variant/40"
          >
            {example}
          </span>
        ))}
      </div>
    </div>
  );
}

function GeneratingState() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-sm px-4">
      <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-5 relative">
        <span
          className="material-symbols-outlined text-primary text-3xl animate-pulse"
          style={{ fontVariationSettings: "'FILL' 0, 'wght' 200" }}
        >
          memory
        </span>
      </div>
      <h2 className="text-lg font-light text-on-surface/80 mb-2">
        Generating Design
      </h2>
      <p className="text-on-surface-variant/50 text-xs">
        Creating schematic and PCB...
      </p>
      <div className="mt-4 flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}
