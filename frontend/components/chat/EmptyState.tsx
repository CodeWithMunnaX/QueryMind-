"use client";

import { useState } from "react";
import { Sparkles, TrendingUp, PieChart, MapPin, Boxes, ChevronDown } from "lucide-react";

const QUICK_START = [
  { icon: TrendingUp, text: "Which category generated the highest revenue in 2025?" },
  { icon: Boxes, text: "Show me the top 5 products by revenue in 2025." },
  { icon: MapPin, text: "What are total sales by region?" },
  { icon: PieChart, text: "Compare sales and profit by category." },
  { icon: TrendingUp, text: "Show monthly sales for 2025." },
  { icon: Sparkles, text: "Which sub-category has the best profit margin?" },
];

const MORE_EXAMPLES = [
  "Which state has the most customers?",
  "What's the average discount by category?",
  "Show me the top 10 customers by total spend.",
  "How does profit vary with discount level?",
  "Which city has the highest average order value?",
  "What were total sales and profit last quarter?",
  "Show me the best products.", // ambiguous — demonstrates the clarification flow
  "Show revenue by department.", // not a real column — demonstrates the hallucination guard
];

export function EmptyState({ onSelect }: { onSelect: (question: string) => void }) {
  const [showMore, setShowMore] = useState(false);

  return (
    <div className="gradient-mesh flex h-full flex-col items-center overflow-y-auto scrollbar-thin px-6 py-10 text-center animate-fade-in">
      <div className="ring-glow mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
        <Sparkles className="h-7 w-7" />
      </div>
      <h2 className="text-2xl font-semibold tracking-tight text-gradient">Ask anything about your sales data</h2>
      <p className="mt-2 max-w-md text-sm text-muted-foreground">
        QueryMind turns your question into SQL, runs it against PostgreSQL, and builds the chart for you.
      </p>

      <div className="mt-9 grid w-full max-w-2xl grid-cols-1 gap-2.5 sm:grid-cols-2">
        {QUICK_START.map(({ icon: Icon, text }, i) => (
          <button
            key={text}
            onClick={() => onSelect(text)}
            style={{ animationDelay: `${i * 60}ms` }}
            className="group flex animate-fade-in items-center gap-3 rounded-xl border border-border bg-card/80 px-4 py-3.5 text-left text-sm shadow-sm backdrop-blur-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/[0.08]"
          >
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
              <Icon className="h-3.5 w-3.5" />
            </div>
            <span className="text-foreground/90 group-hover:text-foreground">{text}</span>
          </button>
        ))}
      </div>

      <div className="mt-6 w-full max-w-2xl">
        <button
          onClick={() => setShowMore((s) => !s)}
          className="mx-auto flex items-center gap-1.5 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
        >
          {showMore ? "Show fewer examples" : "Show more examples"}
          <ChevronDown className={`h-3.5 w-3.5 transition-transform ${showMore ? "rotate-180" : ""}`} />
        </button>

        {showMore && (
          <div className="mt-4 flex flex-wrap justify-center gap-2 animate-fade-in">
            {MORE_EXAMPLES.map((text) => (
              <button
                key={text}
                onClick={() => onSelect(text)}
                className="rounded-full border border-border bg-card/60 px-3.5 py-1.5 text-xs text-muted-foreground backdrop-blur-sm transition-all hover:border-primary/40 hover:bg-card hover:text-foreground"
              >
                {text}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
