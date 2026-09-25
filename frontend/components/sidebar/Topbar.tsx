"use client";

import { useQuery } from "@tanstack/react-query";
import { Circle } from "lucide-react";

import { api } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function Topbar() {
  const { data } = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 60_000,
    retry: false,
  });

  const isOk = data?.status === "ok";

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-border bg-card/60 px-5 backdrop-blur-md">
      <div className="flex items-center gap-2 md:hidden">
        <span className="text-sm font-semibold text-gradient">QueryMind</span>
      </div>
      <div className="hidden text-sm font-medium tracking-tight text-foreground/80 md:block">
        Chat with Your Data
      </div>
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="gap-1.5 py-1">
          <Circle
            className={cn(
              "h-2 w-2",
              isOk ? "fill-[#0ca30c] text-[#0ca30c]" : data ? "fill-amber-500 text-amber-500 animate-pulse-soft" : "fill-muted-foreground text-muted-foreground animate-pulse-soft"
            )}
          />
          {data ? (isOk ? "Connected" : "Degraded") : "Checking…"}
        </Badge>
        <Badge variant="secondary" className="py-1">
          Dataset: Sales
        </Badge>
      </div>
    </header>
  );
}
