"use client";

import type { Message } from "@/lib/types";

interface MessageItemProps {
  message: Message;
}

export default function MessageItem({ message }: MessageItemProps) {
  if (message.type === "system") {
    return (
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 px-1">
          <span className="w-1.5 h-1.5 rounded-full bg-primary/40" />
          <span className="text-[10px] uppercase tracking-[0.25em] text-primary/60 font-bold">
            System Initialization
          </span>
        </div>
        <div className="px-4 py-3 rounded-xl bg-white/[0.02] border border-white/5 text-[13px] text-on-surface-variant/90 leading-relaxed technical-mono">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.type === "user") {
    return (
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 px-1">
          <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant/20" />
          <span className="text-[10px] uppercase tracking-[0.25em] text-on-surface-variant/40 font-bold">
            User Terminal
          </span>
        </div>
        <div className="px-1 text-[15px] text-on-surface leading-relaxed font-medium">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.type === "ai") {
    return (
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 px-1">
          <span
            className={`w-1.5 h-1.5 rounded-full bg-primary ${
              message.isProcessing ? "animate-ping" : ""
            }`}
          />
          <span
            className={`text-[10px] uppercase tracking-[0.25em] font-black ${
              message.isError ? "text-error" : "text-primary"
            }`}
          >
            Genesis AI Analyst
          </span>
        </div>
        <div
          className={`px-4 py-4 rounded-xl border-l-2 text-[13px] leading-relaxed technical-mono space-y-2 ${
            message.isError
              ? "bg-error/5 border-error/40 text-error"
              : "bg-primary/5 border-primary/40 text-on-surface-variant"
          }`}
        >
          {message.isProcessing ? (
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[14px] text-primary animate-spin">
                progress_activity
              </span>
              <span>{message.content}</span>
            </div>
          ) : (
            <AIMessageContent content={message.content} />
          )}
        </div>
      </div>
    );
  }

  return null;
}

function AIMessageContent({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div className="space-y-2">
      {lines.map((line, index) => {
        if (!line.trim()) return <div key={index} className="h-2" />;

        if (line.startsWith("ERC Status: ✓")) {
          return (
            <div key={index} className="flex items-center gap-2 text-green-400">
              <span className="material-symbols-outlined text-[14px]">
                check_circle
              </span>
              <span>{line.replace("ERC Status: ✓ ", "ERC: ")}</span>
            </div>
          );
        }

        if (line.startsWith("ERC Status: ⚠")) {
          return (
            <div key={index} className="flex items-center gap-2 text-yellow-400">
              <span className="material-symbols-outlined text-[14px]">
                warning
              </span>
              <span>{line.replace("ERC Status: ⚠ ", "ERC: ")}</span>
            </div>
          );
        }

        if (line.startsWith("•")) {
          return (
            <div
              key={index}
              className="flex items-start gap-2 pl-4 text-on-surface-variant/70"
            >
              <span className="text-primary/60">→</span>
              <span>{line.substring(2)}</span>
            </div>
          );
        }

        return (
          <div key={index} className="flex items-start gap-2">
            {index === 0 && (
              <span className="material-symbols-outlined text-[14px] text-primary">
                data_exploration
              </span>
            )}
            <span>{line}</span>
          </div>
        );
      })}
    </div>
  );
}
