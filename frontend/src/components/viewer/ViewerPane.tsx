"use client";

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
    <section className="flex-1 relative bg-[#050505] overflow-hidden">
      {/* Grid Background */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage: "radial-gradient(#ffffff 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Main Content Area */}
      <div className="absolute inset-0 flex items-center justify-center p-12">
        {isGenerating ? (
          <GeneratingState />
        ) : projectData ? (
          <div className="relative w-full h-full max-w-[1400px] max-h-[850px] bg-surface-container-low/20 rounded-[3rem] shadow-[0_0_100px_rgba(0,0,0,0.5)] overflow-hidden border border-white/5 backdrop-blur-[2px]">
            <div className="absolute inset-0 bg-[#080808]">
              <KiCanvasEmbed src={currentUrl || ""} />
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
        <div className="absolute top-10 left-10 flex items-center gap-4 glass-panel px-6 py-3 rounded-full border border-primary/20 shadow-2xl">
          <div className="relative flex items-center justify-center">
            <div className="w-2.5 h-2.5 rounded-full bg-primary animate-ping absolute" />
            <div className="w-2.5 h-2.5 rounded-full bg-primary relative" />
          </div>
          <span className="text-[13px] font-semibold tracking-wide text-on-surface/90">
            Generating Circuit Design...
          </span>
        </div>
      )}
    </section>
  );
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-md">
      <div className="w-24 h-24 rounded-3xl bg-primary/5 border border-primary/10 flex items-center justify-center mb-8">
        <span
          className="material-symbols-outlined text-primary/40 text-5xl"
          style={{ fontVariationSettings: "'FILL' 0, 'wght' 200" }}
        >
          developer_board
        </span>
      </div>
      <h2 className="text-2xl font-light text-on-surface/80 mb-4">
        No Design Yet
      </h2>
      <p className="text-on-surface-variant/50 text-sm leading-relaxed">
        Describe your circuit in the chat panel on the left. For example:
        &ldquo;Create a simple LED circuit with a 555 timer for blinking&rdquo;
      </p>
      <div className="mt-8 flex flex-wrap gap-2 justify-center">
        {["LED Circuit", "5V Regulator", "555 Timer", "Line Follower"].map(
          (example) => (
            <span
              key={example}
              className="px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/5 text-xs text-on-surface-variant/40"
            >
              {example}
            </span>
          )
        )}
      </div>
    </div>
  );
}

function GeneratingState() {
  return (
    <div className="flex flex-col items-center justify-center text-center max-w-md">
      <div className="w-24 h-24 rounded-3xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-8 relative">
        <div className="absolute inset-0 rounded-3xl bg-primary/5 animate-ping" />
        <span
          className="material-symbols-outlined text-primary text-5xl animate-pulse"
          style={{ fontVariationSettings: "'FILL' 0, 'wght' 200" }}
        >
          memory
        </span>
      </div>
      <h2 className="text-2xl font-light text-on-surface/80 mb-4">
        Generating Design
      </h2>
      <p className="text-on-surface-variant/50 text-sm leading-relaxed">
        AI is analyzing your request and generating the circuit schematic and PCB layout...
      </p>
      <div className="mt-8 flex items-center gap-3">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-primary/60 animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
        <span className="text-xs text-on-surface-variant/40 technical-mono">
          Processing...
        </span>
      </div>
    </div>
  );
}
