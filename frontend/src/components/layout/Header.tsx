"use client";

interface HeaderProps {
  onDownload?: () => void;
  canDownload?: boolean;
}

export default function Header({ onDownload, canDownload }: HeaderProps) {
  return (
    <header className="h-20 flex items-center justify-between px-10 z-50 bg-black/60 backdrop-blur-2xl border-b border-white/5">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center border border-primary/30">
            <span
              className="material-symbols-outlined text-primary text-xl"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              hexagon
            </span>
          </div>
          <span className="text-on-surface font-semibold text-xl tracking-tight">
            GenAI Genesis
          </span>
        </div>

        <div className="h-6 w-[1px] bg-white/10 mx-2" />

        <nav className="flex items-center gap-6">
          <button className="text-sm font-medium text-on-surface-variant hover:text-on-surface transition-colors">
            Workspace
          </button>
          <button className="text-sm font-medium text-on-surface-variant/60 hover:text-on-surface transition-colors">
            Library
          </button>
          <button className="text-sm font-medium text-on-surface-variant/60 hover:text-on-surface transition-colors">
            Simulations
          </button>
        </nav>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1 mr-6">
          <button className="p-2.5 text-on-surface-variant hover:text-on-surface hover:bg-white/5 rounded-full transition-all">
            <span className="material-symbols-outlined">help</span>
          </button>
          <button className="p-2.5 text-on-surface-variant hover:text-on-surface hover:bg-white/5 rounded-full transition-all">
            <span className="material-symbols-outlined">settings</span>
          </button>
          <button className="p-2.5 text-on-surface-variant hover:text-on-surface hover:bg-white/5 rounded-full transition-all">
            <span className="material-symbols-outlined">notifications</span>
          </button>
        </div>

        <button
          onClick={onDownload}
          disabled={!canDownload}
          className={`px-7 py-2.5 glass-panel rounded-full text-sm font-medium border border-white/10 transition-all ${
            canDownload
              ? "hover:bg-white/5 cursor-pointer"
              : "opacity-50 cursor-not-allowed"
          }`}
        >
          Download
        </button>

        <button
          className={`px-8 py-2.5 primary-glow rounded-full text-on-primary-fixed text-sm font-bold transition-all ${
            canDownload ? "hover:brightness-110" : "opacity-50"
          }`}
          disabled={!canDownload}
        >
          Export
        </button>

        <div className="ml-4 w-10 h-10 rounded-full bg-gradient-to-br from-surface-variant to-surface-container-high border border-white/10" />
      </div>
    </header>
  );
}
