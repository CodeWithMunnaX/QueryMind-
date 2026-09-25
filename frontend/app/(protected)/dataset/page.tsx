"use client";

import { useQuery } from "@tanstack/react-query";
import { Database, Table2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { formatNumber } from "@/lib/utils";

export default function DatasetPage() {
  const { data: datasets, isLoading: loadingDatasets } = useQuery({
    queryKey: ["datasets"],
    queryFn: api.getDatasets,
  });
  const { data: schema, isLoading: loadingSchema } = useQuery({ queryKey: ["schema"], queryFn: api.getSchema });

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="mx-auto max-w-3xl space-y-6 p-6">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Dataset</h1>
          <p className="text-sm text-muted-foreground">The data QueryMind can query — schema retrieved live from PostgreSQL.</p>
        </div>

        {loadingDatasets ? (
          <Skeleton className="h-24" />
        ) : (
          datasets?.map((ds) => (
            <Card key={ds.id}>
              <CardHeader className="flex-row items-center gap-3 space-y-0">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  <Database className="h-4 w-4" />
                </div>
                <div>
                  <CardTitle className="text-sm font-semibold text-foreground">{ds.name}</CardTitle>
                  <p className="text-xs text-muted-foreground">{ds.description}</p>
                </div>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Badge variant="secondary">{formatNumber(ds.row_count)} rows</Badge>
                <Badge variant="outline">table: {ds.table_name}</Badge>
              </CardContent>
            </Card>
          ))
        )}

        <Card>
          <CardHeader className="flex-row items-center gap-2 space-y-0">
            <Table2 className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-semibold text-foreground">Available columns</CardTitle>
          </CardHeader>
          <CardContent>
            {loadingSchema ? (
              <Skeleton className="h-40" />
            ) : (
              <div className="grid grid-cols-2 gap-x-4 gap-y-2 sm:grid-cols-3">
                {schema?.tables.flatMap((t) =>
                  t.columns.map((c) => (
                    <div key={c.name} className="flex items-center justify-between rounded-md bg-muted/50 px-2.5 py-1.5 text-xs">
                      <span className="font-medium text-foreground">{c.name}</span>
                      <span className="text-muted-foreground">{c.type}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
