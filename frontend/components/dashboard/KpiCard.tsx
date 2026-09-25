import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  accent?: string;
}

export function KpiCard({ label, value, icon: Icon, accent = "var(--chart-1)" }: KpiCardProps) {
  return (
    <Card className="card-hover glass gradient-mesh relative overflow-hidden">
      <div
        className="pointer-events-none absolute -right-6 -top-6 h-24 w-24 rounded-full opacity-[0.12] blur-2xl"
        style={{ background: accent }}
      />
      <CardContent className="relative flex items-center gap-4 p-5">
        <div
          className={cn("flex h-11 w-11 shrink-0 items-center justify-center rounded-xl shadow-sm")}
          style={{ background: `color-mix(in oklab, ${accent} 16%, transparent)`, color: accent }}
        >
          <Icon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <p className="text-xs font-medium text-muted-foreground">{label}</p>
          <p className="truncate text-2xl font-semibold tabular-nums tracking-tight">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}
