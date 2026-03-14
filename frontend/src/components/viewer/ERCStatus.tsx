"use client";

import type { ERCResult } from "@/lib/types";

interface ERCStatusProps {
  ercResult?: ERCResult;
  isVisible?: boolean;
}

export default function ERCStatus({ ercResult, isVisible = true }: ERCStatusProps) {
  if (!isVisible || !ercResult) return null;

  return (
    <div
      className={`absolute top-10 left-10 flex items-center gap-4 glass-panel px-6 py-3 rounded-full border shadow-2xl ${
        ercResult.passed
          ? "border-green-500/20"
          : "border-yellow-500/20"
      }`}
    >
      <div className="relative flex items-center justify-center">
        <div
          className={`w-2.5 h-2.5 rounded-full absolute ${
            ercResult.passed ? "bg-green-500" : "bg-yellow-500 animate-ping"
          }`}
        />
        <div
          className={`w-2.5 h-2.5 rounded-full relative ${
            ercResult.passed ? "bg-green-500" : "bg-yellow-500"
          }`}
        />
      </div>
      <span className="text-[13px] font-semibold tracking-wide text-on-surface/90">
        {ercResult.passed ? (
          <>ERC Passed</>
        ) : (
          <>
            ERC: {ercResult.messages?.length || 0} issue
            {(ercResult.messages?.length || 0) !== 1 ? "s" : ""} found
          </>
        )}
      </span>
    </div>
  );
}
