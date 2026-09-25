import { Sparkles } from "lucide-react";

import { Skeleton } from "@/components/ui/skeleton";

export function LoadingBubble() {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="ring-glow flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
        <Sparkles className="h-3.5 w-3.5 animate-pulse-soft" />
      </div>
      <div className="flex-1 space-y-2 rounded-2xl rounded-tl-sm border border-border bg-card p-4">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
        <Skeleton className="h-32 w-full" />
      </div>
    </div>
  );
}
