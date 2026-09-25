"use client";

import { useQuery } from "@tanstack/react-query";
import { CheckCircle2, Info, XCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const { data } = useQuery({ queryKey: ["health"], queryFn: api.health });

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="mx-auto max-w-3xl space-y-6 p-6">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Settings</h1>
          <p className="text-sm text-muted-foreground">System status and configuration.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-semibold text-foreground">System status</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <StatusRow label="Database connection" ok={data?.database === "connected"} detail={data?.database} />
            <Separator />
            <StatusRow label="LLM (OpenAI)" ok={data?.llm === "configured"} detail={data?.llm} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Info className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold text-foreground">About this dataset</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>
              QueryMind is connected to a single read-only analytics dataset (Superstore-style sales
              transactions). Every question is converted to SQL by an LLM, validated for safety and
              schema correctness, and executed as a read-only, time-limited PostgreSQL query — the
              model can never modify data.
            </p>
            <p>
              Model, database, and app configuration are set via backend environment variables
              (<code className="rounded bg-muted px-1 py-0.5 text-xs">OPENAI_MODEL</code>,{" "}
              <code className="rounded bg-muted px-1 py-0.5 text-xs">DATABASE_URL</code>) — see the
              project README.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function StatusRow({ label, ok, detail }: { label: string; ok?: boolean; detail?: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-foreground">{label}</span>
      <Badge variant={ok ? "success" : "destructive"} className="gap-1">
        {ok ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
        {detail ?? "unknown"}
      </Badge>
    </div>
  );
}
