"use client";

import { useRef, useState } from "react";
import { CornerDownLeft, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const submit = () => {
    if (!value.trim() || isLoading) return;
    onSend(value);
    setValue("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  return (
    <div className="border-t border-border bg-card/60 p-4 backdrop-blur-sm">
      <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-border bg-background p-2 shadow-sm transition-shadow focus-within:border-primary/40 focus-within:shadow-md focus-within:shadow-primary/[0.06] focus-within:ring-2 focus-within:ring-ring/40">
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            e.target.style.height = "auto";
            e.target.style.height = `${Math.min(e.target.scrollHeight, 160)}px`;
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask a question about your sales data…"
          className="max-h-40 min-h-[36px] flex-1 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0"
          disabled={isLoading}
        />
        <Button
          onClick={submit}
          disabled={isLoading || !value.trim()}
          size="icon"
          className="mb-1 shrink-0 rounded-xl transition-transform active:scale-95"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <CornerDownLeft className="h-4 w-4" />}
        </Button>
      </div>
      <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-muted-foreground">
        QueryMind only runs read-only queries against your sales data. Enter to send, Shift+Enter for a new line,{" "}
        <kbd className="rounded border border-border bg-muted px-1 font-mono text-[10px]">⌘K</kbd> for a new chat.
      </p>
    </div>
  );
}
