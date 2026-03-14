"use client";

import { useEffect, useRef } from "react";
import MessageItem from "./MessageItem";
import type { Message } from "@/lib/types";

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div
      ref={scrollRef}
      className="p-8 flex-1 flex flex-col custom-scrollbar overflow-y-auto gap-8"
    >
      <div className="space-y-10">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
      </div>
    </div>
  );
}
