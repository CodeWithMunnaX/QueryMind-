"use client";

import { useState } from "react";
import { AlertTriangle, Check, Copy, Download, MessageSquarePlus, RefreshCw, Sparkles, User } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { DynamicChart } from "@/components/charts/DynamicChart";
import { DataTable } from "@/components/tables/DataTable";
import { cn } from "@/lib/utils";
import type { ChatTurn } from "@/types/analytics";

function downloadCsv(columns: string[], rows: Record<string, unknown>[], filename: string) {
  const escape = (v: unknown) => `"${String(v ?? "").replaceAll('"', '""')}"`;
  const header = columns.map(escape).join(",");
  const body = rows.map((r) => columns.map((c) => escape(r[c])).join(",")).join("\n");
  const blob = new Blob([`${header}\n${body}`], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

const FOLLOW_UP_SUGGESTIONS = [
  "What about last year?",
  "Break it down further",
  "Show only the top 5",
  "Compare to the previous quarter",
];

interface ChatMessageProps {
  turn: ChatTurn;
  question?: string;
  onRegenerate?: (question: string) => void;
  onClarify?: (option: string) => void;
  onFollowUp?: (question: string) => void;
}

export function ChatMessage({ turn, question, onRegenerate, onClarify, onFollowUp }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const [sqlOpen, setSqlOpen] = useState(false);

  if (turn.role === "user") {
    return (
      <div className="flex animate-fade-in justify-end gap-3">
        <div className="max-w-xl rounded-2xl rounded-tr-sm bg-gradient-to-br from-primary to-primary/90 px-4 py-2.5 text-sm text-primary-foreground shadow-md shadow-primary/20">
          {turn.content}
        </div>
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground ring-1 ring-border">
          <User className="h-3.5 w-3.5" />
        </div>
      </div>
    );
  }

  const response = turn.response;
  const status = response?.metadata.status;
  const hasChart = response?.chart && response.chart.type !== "none" && response.chart.type !== "table";
  const hasData = response && response.data.length > 0;

  const copySql = async () => {
    if (!response?.sql) return;
    await navigator.clipboard.writeText(response.sql);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className="flex animate-fade-in gap-3">
      <div className="ring-glow flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
        <Sparkles className="h-3.5 w-3.5" />
      </div>

      <div
        className={cn(
          "min-w-0 flex-1 space-y-3 rounded-2xl rounded-tl-sm border p-4 shadow-sm transition-shadow hover:shadow-md",
          turn.isError || status === "error"
            ? "border-destructive/30 bg-destructive/5"
            : status === "unanswerable"
              ? "border-amber-400/30 bg-amber-400/5"
              : "border-border bg-card"
        )}
      >
        <div className="flex items-start gap-2">
          {(turn.isError || status === "error" || status === "unanswerable") && (
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
          )}
          <p className="text-sm leading-relaxed text-foreground">{turn.content}</p>
        </div>

        {status === "clarification_needed" && response?.clarification_options && (
          <div className="flex flex-wrap gap-2 pt-1">
            {response.clarification_options.map((opt) => (
              <button
                key={opt}
                onClick={() => onClarify?.(opt)}
                className="rounded-full border border-primary/30 bg-primary/5 px-3 py-1 text-xs font-medium text-primary transition-colors hover:bg-primary/10"
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {status === "ok" && response && (
          <>
            <div className="flex flex-wrap items-center gap-2 pt-1">
              {response.metadata.row_count !== undefined && response.metadata.row_count !== null && (
                <Badge variant="secondary">{response.metadata.row_count} rows</Badge>
              )}
              {response.metadata.execution_ms !== undefined && response.metadata.execution_ms !== null && (
                <Badge variant="outline">{response.metadata.execution_ms}ms</Badge>
              )}
              {response.chart && response.chart.type !== "none" && (
                <Badge variant="outline" className="capitalize">
                  {response.chart.type.replace("_", " ")} chart
                </Badge>
              )}
            </div>

            {(hasChart || hasData) && (
              <Tabs defaultValue={hasChart ? "chart" : "data"} className="pt-1">
                <TabsList>
                  {hasChart && <TabsTrigger value="chart">Chart</TabsTrigger>}
                  {hasData && <TabsTrigger value="data">Data</TabsTrigger>}
                </TabsList>
                {hasChart && (
                  <TabsContent value="chart">
                    <DynamicChart config={response.chart!} data={response.data} />
                  </TabsContent>
                )}
                {hasData && (
                  <TabsContent value="data">
                    <DataTable columns={response.columns} rows={response.data} />
                  </TabsContent>
                )}
              </Tabs>
            )}

            {response.sql && (
              <Collapsible open={sqlOpen} onOpenChange={setSqlOpen}>
                <CollapsibleTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 px-2 text-xs text-muted-foreground">
                    {sqlOpen ? "Hide SQL" : "Show SQL"}
                  </Button>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <pre className="mt-1 overflow-x-auto rounded-lg bg-secondary/60 p-3 text-xs text-secondary-foreground scrollbar-thin">
                    <code>{response.sql}</code>
                  </pre>
                </CollapsibleContent>
              </Collapsible>
            )}

            <div className="flex flex-wrap items-center gap-1.5 border-t border-border pt-3">
              {response.sql && (
                <Button variant="outline" size="sm" onClick={copySql} className="h-7 text-xs">
                  {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  {copied ? "Copied" : "Copy SQL"}
                </Button>
              )}
              {question && onRegenerate && (
                <Button variant="outline" size="sm" onClick={() => onRegenerate(question)} className="h-7 text-xs">
                  <RefreshCw className="h-3 w-3" />
                  Regenerate
                </Button>
              )}
              {hasData && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => downloadCsv(response.columns, response.data, "querymind-export.csv")}
                  className="h-7 text-xs"
                >
                  <Download className="h-3 w-3" />
                  Download CSV
                </Button>
              )}
            </div>

            {onFollowUp && (
              <div className="flex flex-wrap items-center gap-1.5">
                <MessageSquarePlus className="h-3.5 w-3.5 text-muted-foreground" />
                {FOLLOW_UP_SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => onFollowUp(s)}
                    className="rounded-full border border-dashed border-border px-2.5 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-primary"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
