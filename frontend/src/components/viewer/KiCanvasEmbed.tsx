"use client";

import { useEffect, useRef, useState } from "react";

interface KiCanvasEmbedProps {
  src: string;
  className?: string;
}

export default function KiCanvasEmbed({ src, className = "" }: KiCanvasEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current || !src) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    containerRef.current.innerHTML = "";

    const embed = document.createElement("kicanvas-embed");
    embed.setAttribute("src", src);
    embed.setAttribute("controls", "basic");
    embed.setAttribute("theme", "kicad-dark");
    
    Object.assign(embed.style, {
      width: "100%",
      height: "100%",
      display: "block",
      background: "#080808",
    });

    containerRef.current.appendChild(embed);

    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);

    return () => clearTimeout(timer);
  }, [src]);

  if (!src) {
    return (
      <div className={`w-full h-full flex items-center justify-center bg-[#080808] ${className}`}>
        <span className="technical-mono text-xs text-on-surface-variant/30">
          No file loaded
        </span>
      </div>
    );
  }

  return (
    <div className={`w-full h-full relative bg-[#080808] ${className}`}>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#080808] z-10">
          <div className="flex flex-col items-center gap-2">
            <span className="material-symbols-outlined text-primary/60 text-2xl animate-spin">
              progress_activity
            </span>
            <span className="technical-mono text-[10px] text-on-surface-variant/40">
              Loading viewer...
            </span>
          </div>
        </div>
      )}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
}
