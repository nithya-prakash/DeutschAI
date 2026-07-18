"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { useRequireAuth } from "@/hooks/use-require-auth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isReady } = useRequireAuth();

  if (!isReady) {
    return <div className="flex min-h-screen items-center justify-center text-muted-foreground">Loading…</div>;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <header className="flex items-center justify-end border-b border-border px-8 py-4">
          <ThemeToggle />
        </header>
        <main className="mx-auto max-w-5xl px-8 py-8">{children}</main>
      </div>
    </div>
  );
}
