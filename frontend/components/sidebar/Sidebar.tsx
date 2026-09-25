"use client";

import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { LayoutDashboard, MessageSquare, History, Database, Settings, Sparkles, LogOut } from "lucide-react";

import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/app", label: "Ask Data", icon: MessageSquare },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/history", label: "Query History", icon: History },
  { href: "/dataset", label: "Dataset", icon: Database },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  return (
    <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card/40 backdrop-blur-sm md:flex">
      <div className="flex h-14 items-center gap-2.5 border-b border-border px-5">
        <div className="ring-glow flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
          <Sparkles className="h-4 w-4" />
        </div>
        <span className="text-sm font-semibold tracking-tight text-gradient">QueryMind</span>
      </div>

      <nav className="flex flex-1 flex-col gap-0.5 p-3">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all duration-200",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:translate-x-0.5 hover:bg-accent hover:text-accent-foreground"
              )}
            >
              {active && (
                <span className="absolute -left-3 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-primary" />
              )}
              <Icon className={cn("h-4 w-4 transition-transform duration-200", active && "scale-110")} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mx-3 mb-3 space-y-2">
        <div className="rounded-xl border border-border bg-gradient-to-br from-accent/60 to-transparent p-3.5 text-xs text-muted-foreground">
          <p className="font-medium text-foreground">Superstore Sales</p>
          <p>Live PostgreSQL analytics</p>
        </div>
        {user && (
          <button
            onClick={() => {
              logout();
              router.push("/");
            }}
            className="group flex w-full items-center gap-2.5 rounded-xl border border-border px-3 py-2.5 text-left text-xs transition-colors hover:border-destructive/40 hover:bg-destructive/5"
          >
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[10px] font-semibold text-primary">
              {user.email[0]?.toUpperCase()}
            </div>
            <span className="min-w-0 flex-1 truncate text-muted-foreground group-hover:text-foreground">
              {user.email}
            </span>
            <LogOut className="h-3.5 w-3.5 shrink-0 text-muted-foreground group-hover:text-destructive" />
          </button>
        )}
      </div>
    </aside>
  );
}
