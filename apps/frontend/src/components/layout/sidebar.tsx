"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BookOpenText,
  CalendarClock,
  LayoutDashboard,
  ListChecks,
  LogOut,
  MessageCircleQuestion,
  Mic,
  Settings,
  SquareCheckBig,
  UserRound,
} from "lucide-react";

import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/vocabulary", label: "Vocabulary", icon: BookOpenText },
  { href: "/curriculum", label: "Curriculum", icon: ListChecks },
  { href: "/planner", label: "Planner", icon: CalendarClock },
  { href: "/tutor", label: "Tutor", icon: MessageCircleQuestion },
  { href: "/conversation", label: "Conversation", icon: Mic },
  { href: "/quiz", label: "Quiz", icon: SquareCheckBig },
  { href: "/profile", label: "Profile", icon: UserRound },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const logout = useAuthStore((s) => s.logout);
  const user = useAuthStore((s) => s.user);

  return (
    <aside className="flex h-screen w-60 shrink-0 flex-col border-r border-border bg-card px-4 py-6">
      <div className="mb-8 px-2">
        <p className="text-lg font-semibold">DeutschAI</p>
        <p className="text-xs text-muted-foreground">A1 → C1, personalized</p>
      </div>

      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors hover:bg-secondary",
              pathname === href ? "bg-secondary text-foreground" : "text-muted-foreground"
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>

      <div className="mt-auto border-t border-border pt-4">
        {user && (
          <p className="mb-2 truncate px-3 text-xs text-muted-foreground">{user.email}</p>
        )}
        <button
          onClick={() => {
            logout();
            router.push("/login");
          }}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-secondary"
        >
          <LogOut className="h-4 w-4" />
          Log out
        </button>
      </div>
    </aside>
  );
}
