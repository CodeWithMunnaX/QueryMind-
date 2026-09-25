import { Sidebar } from "@/components/sidebar/Sidebar";
import { Topbar } from "@/components/sidebar/Topbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="gradient-mesh flex h-dvh w-full overflow-hidden bg-background">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar />
        <main className="min-h-0 flex-1 overflow-hidden">{children}</main>
      </div>
    </div>
  );
}
