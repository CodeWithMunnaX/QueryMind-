"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { AlertCircle, CheckCircle2, HelpCircle, History as HistoryIcon, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";

const STATUS_META: Record<string, { icon: typeof CheckCircle2; className: string }> = {
  ok: { icon: CheckCircle2, className: "text-[#0ca30c]" },
  clarification_needed: { icon: HelpCircle, className: "text-[#eda100]" },
  unanswerable: { icon: AlertCircle, className: "text-[#eda100]" },
  error: { icon: XCircle, className: "text-destructive" },
};

export default function HistoryPage() {
  const router = useRouter();
  const { data, isLoading } = useQuery({ queryKey: ["history"], queryFn: () => api.getHistory() });

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="mx-auto max-w-3xl space-y-4 p-6">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Query History</h1>
          <p className="text-sm text-muted-foreground">Click a previous question to reopen it in the chat.</p>
        </div>

        {isLoading && (
          <div className="space-y-2">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        )}

        {!isLoading && data?.items.length === 0 && (
          <Card className="flex flex-col items-center gap-2 p-10 text-center text-sm text-muted-foreground">
            <HistoryIcon className="h-6 w-6" />
            No questions asked yet. Head to Ask Data to get started.
          </Card>
        )}

        <div className="space-y-2">
          {data?.items.map((item) => {
            const meta = STATUS_META[item.status] ?? STATUS_META.ok;
            const Icon = meta.icon;
            return (
              <button
                key={item.id}
                onClick={() => router.push(`/app?q=${encodeURIComponent(item.question)}`)}
                className="flex w-full items-start gap-3 rounded-xl border border-border bg-card p-4 text-left text-sm shadow-sm transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-md"
              >
                <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${meta.className}`} />
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium text-foreground">{item.question}</p>
                  {item.answer && <p className="mt-0.5 line-clamp-1 text-xs text-muted-foreground">{item.answer}</p>}
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1">
                  {item.chart_type && item.chart_type !== "none" && (
                    <Badge variant="outline" className="capitalize">
                      {item.chart_type.replace("_", " ")}
                    </Badge>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
