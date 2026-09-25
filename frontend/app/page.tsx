"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Database,
  History,
  MessageSquare,
  ShieldCheck,
  Sparkles,
  Wand2,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";

const FEATURES = [
  {
    icon: Wand2,
    title: "Ask in plain English",
    description:
      "\"Which category made the most money last year?\" — no SQL, no dashboards to build. QueryMind writes the query for you.",
  },
  {
    icon: ShieldCheck,
    title: "Validated, read-only SQL",
    description:
      "Every generated query is parsed and checked before it runs — no writes, no unknown tables or columns, no unbounded results.",
  },
  {
    icon: BarChart3,
    title: "Auto-selected charts",
    description:
      "Bar, line, pie, or scatter — picked automatically from the shape of your data, never pointed at a column that doesn't exist.",
  },
  {
    icon: MessageSquare,
    title: "Follow-up questions",
    description: "\"What about last year?\" just works — QueryMind remembers the context of your conversation.",
  },
  {
    icon: Database,
    title: "Live dashboard",
    description: "KPIs, trends, and top performers computed straight from PostgreSQL — nothing hardcoded.",
  },
  {
    icon: History,
    title: "Query history",
    description: "Every question is saved. Click any past question to reopen its answer, chart, and SQL instantly.",
  },
];

const STEPS = [
  { n: "01", title: "Ask a question", detail: "Type a question about your data, just like you'd ask a colleague." },
  { n: "02", title: "QueryMind writes & checks the SQL", detail: "An LLM drafts the query; a safety layer validates it before anything runs." },
  { n: "03", title: "Get your answer", detail: "A plain-English summary, the exact SQL, the data, and a chart — all in one place." },
];

export default function LandingPage() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-dvh bg-background">
      {/* Nav */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2.5">
            <div className="ring-glow flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
              <Sparkles className="h-4 w-4" />
            </div>
            <span className="text-base font-semibold tracking-tight text-gradient">QueryMind</span>
          </div>
          <div className="flex items-center gap-2">
            {isAuthenticated ? (
              <Button asChild size="sm">
                <Link href="/app">
                  Go to app <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </Button>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/login">Log in</Link>
                </Button>
                <Button asChild size="sm">
                  <Link href="/register">Get started free</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="gradient-mesh relative overflow-hidden border-b border-border px-6 py-24 text-center">
        <div className="mx-auto max-w-3xl animate-fade-in">
          <div className="mx-auto mb-6 flex w-fit items-center gap-2 rounded-full border border-border bg-card/80 px-3.5 py-1.5 text-xs font-medium text-muted-foreground shadow-sm backdrop-blur-sm">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            AI-powered analytics, backed by validated SQL
          </div>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-6xl">
            Chat with your data.
            <br />
            <span className="text-gradient">Get real answers.</span>
          </h1>
          <p className="mx-auto mt-6 max-w-xl text-lg text-muted-foreground">
            Ask plain-English questions about your sales data and get instant, accurate answers —
            backed by real SQL, live charts, and a database that never gets touched unsafely.
          </p>
          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            <Button asChild size="lg" className="shadow-lg shadow-primary/20">
              <Link href={isAuthenticated ? "/app" : "/register"}>
                {isAuthenticated ? "Go to app" : "Get started free"}
                <ArrowRight className="h-4 w-4" />
              </Link>
            </Button>
            {!isAuthenticated && (
              <Button asChild variant="outline" size="lg">
                <Link href="/login">Log in</Link>
              </Button>
            )}
          </div>
        </div>

        {/* Mock chat preview */}
        <div className="mx-auto mt-16 max-w-2xl animate-fade-in text-left" style={{ animationDelay: "150ms" }}>
          <Card className="glass overflow-hidden shadow-xl">
            <CardContent className="space-y-3 p-5">
              <div className="flex justify-end">
                <div className="rounded-2xl rounded-tr-sm bg-gradient-to-br from-primary to-primary/90 px-4 py-2 text-sm text-primary-foreground shadow-md shadow-primary/20">
                  Which category generated the highest revenue in 2025?
                </div>
              </div>
              <div className="flex gap-2.5">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
                  <Sparkles className="h-3 w-3" />
                </div>
                <div className="flex-1 space-y-2 rounded-2xl rounded-tl-sm border border-border bg-card p-3 text-left text-sm">
                  <p>Technology generated the highest revenue in 2025, totaling $3.98M.</p>
                  <div className="flex h-16 items-end gap-1.5 pt-1">
                    {[95, 62, 40].map((h, i) => (
                      <div
                        key={i}
                        className="flex-1 rounded-t-sm"
                        style={{ height: `${h}%`, background: `var(--chart-${i + 1})` }}
                      />
                    ))}
                  </div>
                  <code className="block truncate rounded bg-secondary/60 px-2 py-1 text-[10px] text-secondary-foreground">
                    SELECT category, SUM(sales) AS total_sales FROM sales WHERE ...
                  </code>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-6xl px-6 py-20">
        <div className="mx-auto max-w-xl text-center">
          <h2 className="text-3xl font-semibold tracking-tight">Everything you need, nothing risky</h2>
          <p className="mt-3 text-muted-foreground">
            Built like a production system, not a demo — every layer guards against the model getting it wrong.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, description }, i) => (
            <Card
              key={title}
              className="card-hover animate-fade-in"
              style={{ animationDelay: `${i * 70}ms` }}
            >
              <CardContent className="p-6">
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                  <Icon className="h-5 w-5" />
                </div>
                <h3 className="font-semibold text-foreground">{title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-border bg-card/30 px-6 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-3xl font-semibold tracking-tight">How it works</h2>
          <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-3">
            {STEPS.map((step) => (
              <div key={step.n} className="relative">
                <span className="text-gradient text-4xl font-bold opacity-40">{step.n}</span>
                <h3 className="mt-2 font-semibold text-foreground">{step.title}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground">{step.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="gradient-mesh px-6 py-24 text-center">
        <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">Ready to talk to your data?</h2>
        <p className="mx-auto mt-3 max-w-md text-muted-foreground">
          Create a free account and ask your first question in under a minute.
        </p>
        <div className="mt-8">
          <Button asChild size="lg" className="shadow-lg shadow-primary/20">
            <Link href={isAuthenticated ? "/app" : "/register"}>
              {isAuthenticated ? "Go to app" : "Get started free"}
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      <footer className="border-t border-border px-6 py-8 text-center text-xs text-muted-foreground">
        QueryMind — built with Next.js, FastAPI, LangChain &amp; OpenAI.
      </footer>
    </div>
  );
}
