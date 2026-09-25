"use client";

import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  BarChart3,
  DollarSign,
  LineChart,
  type LucideIcon,
  Package,
  PieChart,
  ShoppingCart,
  Table2,
  TrendingUp,
  Users,
} from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { DynamicChart } from "@/components/charts/DynamicChart";
import { DataTable } from "@/components/tables/DataTable";
import { api, ApiError } from "@/lib/api";
import { formatCurrency, formatNumber } from "@/lib/utils";

import { KpiCard } from "./KpiCard";

export function DashboardView() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["dashboard"],
    queryFn: api.getDashboard,
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 p-6 sm:grid-cols-2 lg:grid-cols-5">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24" />
        ))}
        <Skeleton className="col-span-full h-80" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center">
        <AlertCircle className="h-8 w-8 text-destructive" />
        <p className="text-sm text-muted-foreground">
          {error instanceof ApiError ? error.message : "Could not load dashboard metrics."}
        </p>
      </div>
    );
  }

  const { metrics, sales_over_time, sales_by_region, sales_by_category, top_products } = data;

  return (
    <div className="h-full overflow-y-auto scrollbar-thin">
      <div className="mx-auto max-w-7xl space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-gradient">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Live metrics computed directly from PostgreSQL — nothing here is hardcoded.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          <KpiCard label="Total Sales" value={formatCurrency(metrics.total_sales, { compact: true })} icon={DollarSign} accent="var(--chart-1)" />
          <KpiCard label="Total Profit" value={formatCurrency(metrics.total_profit, { compact: true })} icon={TrendingUp} accent="var(--chart-3)" />
          <KpiCard label="Total Orders" value={formatNumber(metrics.total_orders)} icon={ShoppingCart} accent="var(--chart-2)" />
          <KpiCard label="Total Customers" value={formatNumber(metrics.total_customers)} icon={Users} accent="var(--chart-7)" />
          <KpiCard label="Avg Order Value" value={formatCurrency(metrics.average_order_value)} icon={Package} accent="var(--chart-4)" />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <Card className="card-hover lg:col-span-2">
            <ChartHeader icon={LineChart} title="Sales Over Time" />
            <CardContent>
              <DynamicChart config={{ type: "line", x: "month", y: "total_sales", title: "" }} data={sales_over_time} />
            </CardContent>
          </Card>

          <Card className="card-hover">
            <ChartHeader icon={PieChart} title="Sales by Category" />
            <CardContent>
              <DynamicChart config={{ type: "pie", x: "category", y: "total_sales", title: "" }} data={sales_by_category} />
            </CardContent>
          </Card>

          <Card className="card-hover">
            <ChartHeader icon={BarChart3} title="Sales by Region" />
            <CardContent>
              <DynamicChart config={{ type: "bar", x: "region", y: "total_sales", title: "" }} data={sales_by_region} />
            </CardContent>
          </Card>

          <Card className="card-hover lg:col-span-2">
            <ChartHeader icon={Table2} title="Top Products" />
            <CardContent>
              <DataTable columns={["product_name", "total_sales", "total_profit"]} rows={top_products} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function ChartHeader({ icon: Icon, title }: { icon: LucideIcon; title: string }) {
  return (
    <CardHeader className="flex-row items-center gap-2.5 space-y-0">
      <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
        <Icon className="h-3.5 w-3.5" />
      </div>
      <CardTitle className="text-sm font-semibold text-foreground">{title}</CardTitle>
    </CardHeader>
  );
}
