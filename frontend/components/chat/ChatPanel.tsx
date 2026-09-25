"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { PlusCircle } from "lucide-react";

import { useChat } from "@/hooks/useChat";
import { Button } from "@/components/ui/button";
import { genId } from "@/lib/utils";
import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";
import { EmptyState } from "./EmptyState";
import { LoadingBubble } from "./LoadingBubble";

export function ChatPanel() {
  const [conversationId, setConversationId] = useState(() => genId("conv"));
  const { turns, ask, isLoading, reset } = useChat(conversationId);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputContainerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const searchParams = useSearchParams();

  const newChat = useCallback(() => {
    reset();
    setConversationId(genId("conv"));
  }, [reset]);

  // Supports "reopen from history": /app?q=<question> triggers a fresh ask() then clears the param.
  useEffect(() => {
    const replayQuestion = searchParams.get("q");
    if (replayQuestion) {
      ask(replayQuestion);
      router.replace("/app");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, isLoading]);

  // Ctrl/Cmd+K — start a new chat (also clears backend conversation context).
  // Ctrl/Cmd+/ — focus the question input from anywhere on the page.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const isMeta = e.metaKey || e.ctrlKey;
      if (isMeta && e.key.toLowerCase() === "k") {
        e.preventDefault();
        newChat();
      } else if (isMeta && e.key === "/") {
        e.preventDefault();
        inputContainerRef.current?.querySelector("textarea")?.focus();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [newChat]);

  return (
    <div className="flex h-full flex-col">
      {turns.length > 0 && (
        <div className="flex items-center justify-end border-b border-border px-4 py-2">
          <Button variant="ghost" size="sm" onClick={newChat} className="h-7 gap-1.5 text-xs text-muted-foreground">
            <PlusCircle className="h-3.5 w-3.5" />
            New chat
            <kbd className="ml-1 rounded border border-border bg-muted px-1 font-mono text-[10px]">⌘K</kbd>
          </Button>
        </div>
      )}
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto scrollbar-thin">
        {turns.length === 0 ? (
          <EmptyState onSelect={ask} />
        ) : (
          <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
            {turns.map((turn, i) => {
              const precedingUserTurn =
                turn.role === "assistant"
                  ? [...turns.slice(0, i)].reverse().find((t) => t.role === "user")
                  : undefined;
              return (
                <ChatMessage
                  key={turn.id}
                  turn={turn}
                  question={precedingUserTurn?.content}
                  onRegenerate={ask}
                  onClarify={ask}
                  onFollowUp={ask}
                />
              );
            })}
            {isLoading && <LoadingBubble />}
          </div>
        )}
      </div>
      <div ref={inputContainerRef}>
        <ChatInput onSend={ask} isLoading={isLoading} />
      </div>
    </div>
  );
}
