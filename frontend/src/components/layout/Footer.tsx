"use client";

interface FooterProps {
  isConnected?: boolean;
  isGenerating?: boolean;
}

export default function Footer({
  isConnected = true,
  isGenerating = false,
}: FooterProps) {
  return (
    <footer className="h-10 bg-black border-t border-white/5 px-10 flex items-center justify-between z-50">
      <div className="flex items-center gap-10">
        <div className="flex items-center gap-2.5">
          <span
            className={`material-symbols-outlined text-sm ${
              isConnected ? "text-primary" : "text-error"
            }`}
          >
            sensors
          </span>
          <span className="text-[11px] text-on-surface-variant font-semibold tracking-wide uppercase">
            {isConnected ? "Backend: Connected" : "Backend: Disconnected"}
          </span>
        </div>

        <div className="flex items-center gap-2.5">
          <span className="material-symbols-outlined text-sm text-on-surface-variant/40">
            memory
          </span>
          <span className="text-[11px] text-on-surface-variant font-medium technical-mono tracking-tighter">
            {isGenerating ? "Processing..." : "Ready"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <div
            className={`w-1.5 h-1.5 rounded-full ${
              isGenerating ? "bg-primary animate-pulse" : "bg-green-500/50"
            }`}
          />
          <span className="text-[11px] text-on-surface-variant/40">
            {isGenerating ? "Generating" : "Engine: Stable"}
          </span>
        </div>
        <span className="text-[11px] font-black text-primary/80 tracking-widest">
          v1.0.0
        </span>
      </div>
    </footer>
  );
}
