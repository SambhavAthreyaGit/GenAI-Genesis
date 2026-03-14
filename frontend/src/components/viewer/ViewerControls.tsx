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
      {/* View Toggle - Bottom Right */}
      <div className="absolute bottom-4 right-4 z-20">
        <div className="flex glass-panel rounded-lg p-0.5 border border-white/10 shadow-xl">
          <button
            onClick={() => onViewChange("schematic")}
            className={`px-3 py-1.5 rounded-md text-[11px] font-semibold transition-all flex items-center gap-1.5 ${
              activeView === "schematic"
                ? "bg-primary/20 text-primary"
                : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">schema</span>
            Schematic
          </button>
          <button
            onClick={() => onViewChange("pcb")}
            className={`px-3 py-1.5 rounded-md text-[11px] font-semibold transition-all flex items-center gap-1.5 ${
              activeView === "pcb"
                ? "bg-tertiary/20 text-tertiary"
                : "text-on-surface-variant hover:text-on-surface hover:bg-white/5"
            }`}
          >
            <span className="material-symbols-outlined text-[14px]">developer_board</span>
            PCB
          </button>
        </div>
      </div>

      {/* Project Info - Top Right */}
      <div className="absolute top-4 right-4 text-right z-20">
        <div className="text-[9px] text-on-surface-variant/50 font-bold uppercase tracking-wider mb-0.5">
          {activeView === "schematic" ? "Schematic" : "PCB Layout"}
        </div>
        <div className="text-sm font-light text-on-surface/80 tracking-tight">
          {projectName?.slice(0, 8) || "Design"}
          <span className="text-primary/60">
            .{activeView === "schematic" ? "sch" : "pcb"}
          </span>
        </div>
      </div>
    </>
  );
}
