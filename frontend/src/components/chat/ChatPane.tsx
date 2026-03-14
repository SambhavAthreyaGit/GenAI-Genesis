"use client";

import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import type { Message } from "@/lib/types";

interface ChatPaneProps {
  messages: Message[];
  onGenerate: (prompt: string) => void;
  isGenerating?: boolean;
}

export default function ChatPane({
  messages,
  onGenerate,
  isGenerating = false,
}: ChatPaneProps) {
  return (
    <aside className="w-[420px] flex flex-col z-40 border-r border-white/5 bg-black/20 backdrop-blur-xl">
      <MessageList messages={messages} />
      <ChatInput
        onSubmit={onGenerate}
        disabled={isGenerating}
        placeholder={
          isGenerating
            ? "Generating design..."
            : "Describe your circuit (e.g., 'Simple LED circuit with 5V regulator')"
        }
      />
    </aside>
  );
}
