"use client";

import { useState, useCallback, KeyboardEvent } from "react";

interface ChatInputProps {
  onSubmit: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({
  onSubmit,
  disabled = false,
  placeholder = "Describe your circuit...",
}: ChatInputProps) {
  const [input, setInput] = useState("");

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (trimmed && !disabled) {
      onSubmit(trimmed);
      setInput("");
    }
  }, [input, disabled, onSubmit]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="p-8 border-t border-white/5 bg-black/40">
      <div className="relative flex items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className="w-full bg-white/[0.03] border border-white/10 rounded-2xl py-4 pl-5 pr-14 text-sm text-on-surface placeholder-on-surface-variant/30 focus:ring-1 focus:ring-primary/40 focus:bg-white/[0.05] transition-all outline-none disabled:opacity-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSubmit}
          disabled={disabled || !input.trim()}
          className="absolute right-2 p-2.5 primary-glow rounded-xl hover:scale-105 transition-all flex items-center justify-center disabled:opacity-50 disabled:hover:scale-100 disabled:cursor-not-allowed"
        >
          <span
            className="material-symbols-outlined text-on-primary-fixed text-[20px]"
            style={{ fontVariationSettings: "'FILL' 1" }}
          >
            bolt
          </span>
        </button>
      </div>

      <div className="flex items-center gap-6 mt-6 px-2">
        <button className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-on-surface-variant/40 hover:text-primary transition-colors font-bold">
          <span className="material-symbols-outlined text-[16px]">layers</span>
          Stackup
        </button>
        <button className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-on-surface-variant/40 hover:text-primary transition-colors font-bold">
          <span className="material-symbols-outlined text-[16px]">
            analytics
          </span>
          DRC Check
        </button>
        <button className="flex items-center gap-2 text-[10px] uppercase tracking-widest text-on-surface-variant/40 hover:text-primary transition-colors font-bold ml-auto">
          <span className="material-symbols-outlined text-[16px]">
            terminal
          </span>
          Live Logs
        </button>
      </div>
    </div>
  );
}
