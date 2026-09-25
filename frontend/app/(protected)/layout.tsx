"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Sparkles } from "lucide-react";

import { AppShell } from "@/components/sidebar/AppShell";
import { useAuth } from "@/hooks/useAuth";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="flex h-dvh w-full flex-col items-center justify-center gap-3 bg-background">
        <div className="ring-glow flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary to-[#4a3aa7] text-primary-foreground">
          <Sparkles className="h-6 w-6" />
        </div>
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return <AppShell>{children}</AppShell>;
}
