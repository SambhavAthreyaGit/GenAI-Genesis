"use client";

interface ViewerControlsProps {
  activeView: "schematic" | "pcb";
  onViewChange: (view: "schematic" | "pcb") => void;
  projectName?: string;
}

export default function ViewerControls({
  activeView,
  onViewChange,
  projectName,
}: ViewerControlsProps) {
  return (
    <>
      {/* Floating Viewport Controls */}
      <div className="absolute bottom-10 right-10 flex flex-col gap-4">
        <div className="flex flex-col glass-panel rounded-2xl p-1.5 border border-white/10 shadow-2xl">
          <button
            onClick={() => onViewChange("schematic")}
            className={`p-4 rounded-xl transition-all ${
              activeView === "schematic"
                ? "bg-primary/20 text-primary"
                : "text-on-surface hover:bg-white/10"
            }`}
            title="Schematic View"
          >
            <span className="material-symbols-outlined">schema</span>
          </button>
          <div className="h-[1px] w-8 mx-auto bg-white/10" />
          <button
            onClick={() => onViewChange("pcb")}
            className={`p-4 rounded-xl transition-all ${
              activeView === "pcb"
                ? "bg-primary/20 text-primary"
                : "text-on-surface hover:bg-white/10"
            }`}
            title="PCB View"
          >
            <span className="material-symbols-outlined">developer_board</span>
          </button>
        </div>

        <button
          className="p-4 glass-panel rounded-2xl border border-white/10 text-on-surface hover:bg-white/10 transition-all shadow-2xl"
          title="Fit to View"
        >
          <span className="material-symbols-outlined">fit_screen</span>
        </button>
      </div>

      {/* Board Info Overlay */}
      <div className="absolute top-12 right-16 text-right">
        <div className="text-[11px] text-on-surface-variant font-black uppercase tracking-[0.3em] opacity-40 mb-1">
          {activeView === "schematic" ? "Schematic" : "PCB Layout"}
        </div>
        <div className="text-3xl font-light text-on-surface tracking-tight">
          {projectName ? (
            <>
              {projectName.split("_")[0]}
              <span className="text-primary/80">
                .{activeView === "schematic" ? "sch" : "pcb"}
              </span>
            </>
          ) : (
            <>
              Design<span className="text-primary/80">.preview</span>
            </>
          )}
        </div>
        <div className="mt-6 flex flex-col gap-2 items-end">
          <div
            className={`px-3 py-1.5 rounded-lg text-[10px] font-black border flex items-center gap-2 ${
              activeView === "schematic"
                ? "bg-secondary-container/10 text-secondary border-secondary/20"
                : "bg-tertiary/10 text-tertiary border-tertiary/20"
            }`}
          >
            <span
              className={`w-1 h-1 rounded-full ${
                activeView === "schematic" ? "bg-secondary" : "bg-tertiary"
              }`}
            />
            {activeView === "schematic" ? "SCHEMATIC" : "PCB LAYOUT"}
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-white/[0.03] text-on-surface-variant text-[10px] font-black border border-white/5 flex items-center gap-2">
            <span className="w-1 h-1 rounded-full bg-on-surface-variant/40" />
            KICAD FORMAT
          </div>
        </div>
      </div>
    </>
  );
}
