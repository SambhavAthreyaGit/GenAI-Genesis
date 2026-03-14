"use client";

import { useState } from "react";
import type { ERCResult } from "@/lib/types";

interface ERCStatusProps {
  ercResult?: ERCResult;
}

export default function ERCStatus({ ercResult }: ERCStatusProps) {
  const [expanded, setExpanded] = useState(false);

  if (!ercResult) return null;

  const hasRealErrors = ercResult.messages?.some(
    (m) => !m.toLowerCase().includes("failed to load") && 
           !m.toLowerCase().includes("not found") &&
           m.trim().length > 0
  );

  const displayPassed = ercResult.passed || !hasRealErrors;

  return (
    <div className="absolute top-4 left-4 z-20">
      <button
        onClick={() => setExpanded(!expanded)}
        className={`flex items-center gap-2 glass-panel px-3 py-1.5 rounded-full border shadow-lg transition-all hover:bg-white/5 ${
          displayPassed ? "border-green-500/20" : "border-yellow-500/20"
        }`}
      >
        <div
          className={`w-1.5 h-1.5 rounded-full ${
            displayPassed ? "bg-green-500" : "bg-yellow-500"
          }`}
        />
        <span className="text-[11px] font-medium text-on-surface/80">
          {displayPassed ? "ERC OK" : `ERC: ${ercResult.messages?.length || 0} warnings`}
        </span>
        {!displayPassed && (
          <span className="material-symbols-outlined text-[12px] text-on-surface-variant/50">
            {expanded ? "expand_less" : "expand_more"}
          </span>
        )}
      </button>

      {expanded && !displayPassed && ercResult.messages && (
        <div className="mt-2 glass-panel rounded-lg border border-white/10 p-3 max-w-xs shadow-xl">
          <div className="text-[10px] text-on-surface-variant/60 space-y-1 max-h-32 overflow-y-auto custom-scrollbar">
            {ercResult.messages.slice(0, 5).map((msg, i) => (
              <div key={i} className="flex items-start gap-1.5">
                <span className="text-yellow-500/60">•</span>
                <span className="leading-tight">{msg}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
