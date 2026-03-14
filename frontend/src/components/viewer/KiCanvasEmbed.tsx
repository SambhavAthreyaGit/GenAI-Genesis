"use client";

import { useEffect, useRef } from "react";

interface KiCanvasEmbedProps {
  src: string;
  className?: string;
}

export default function KiCanvasEmbed({ src, className = "" }: KiCanvasEmbedProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current && src) {
      containerRef.current.innerHTML = "";
      
      const embed = document.createElement("kicanvas-embed");
      embed.setAttribute("src", src);
      embed.setAttribute("controls", "full");
      embed.setAttribute("theme", "kicad-dark");
      embed.style.width = "100%";
      embed.style.height = "100%";
      
      containerRef.current.appendChild(embed);
    }
  }, [src]);

  return (
    <div ref={containerRef} className={`w-full h-full ${className}`}>
      {!src && (
        <div className="w-full h-full flex items-center justify-center text-on-surface-variant/40">
          <span className="technical-mono text-sm">No file loaded</span>
        </div>
      )}
    </div>
  );
}
