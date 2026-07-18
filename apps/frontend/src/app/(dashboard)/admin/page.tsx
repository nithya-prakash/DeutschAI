"use client";

import { ErrorLogsTable } from "@/components/admin/error-logs-table";
import { LLMUsagePanel } from "@/components/admin/llm-usage-panel";
import { SystemHealthPanel } from "@/components/admin/system-health-panel";
import { UsersTable } from "@/components/admin/users-table";
import { StatTile } from "@/components/dashboard/stat-tile";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  useAdminErrorLogs,
  useAdminLLMUsage,
  useAdminSessionActivity,
  useAdminSystemHealth,
  useAdminUsers,
} from "@/hooks/use-admin";
import { useRequireSuperuser } from "@/hooks/use-require-superuser";

export default function AdminPage() {
  const { isReady } = useRequireSuperuser();
  const { data: users, isLoading: usersLoading } = useAdminUsers();
  const { data: health, isLoading: healthLoading } = useAdminSystemHealth();
  const { data: usage, isLoading: usageLoading } = useAdminLLMUsage();
  const { data: activity, isLoading: activityLoading } = useAdminSessionActivity();
  const { data: errorLogs, isLoading: errorLogsLoading } = useAdminErrorLogs();

  if (!isReady) {
    return <p className="text-muted-foreground">Loading…</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Admin</h1>
        <p className="text-sm text-muted-foreground">
          Users, system health, LLM usage, session activity, and error logs — every value here is
          real data or a real reachability check, never a placeholder.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <StatTile
          label="Sessions today"
          value={activityLoading ? "—" : String(activity?.sessions_today ?? 0)}
        />
        <StatTile
          label="Sessions this week"
          value={activityLoading ? "—" : String(activity?.sessions_this_week ?? 0)}
        />
        <StatTile
          label="Active users this week"
          value={activityLoading ? "—" : String(activity?.active_users_this_week ?? 0)}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System health</CardTitle>
          <CardDescription>Real reachability checks, run at request time.</CardDescription>
        </CardHeader>
        <CardContent>
          {healthLoading || !health ? (
            <p className="text-sm text-muted-foreground">Checking…</p>
          ) : (
            <SystemHealthPanel health={health} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>LLM token usage</CardTitle>
          <CardDescription>
            Real token counts from Claude&apos;s API responses, not an estimated dollar figure.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {usageLoading || !usage ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : (
            <LLMUsagePanel usage={usage} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>Every registered account.</CardDescription>
        </CardHeader>
        <CardContent>
          {usersLoading || !users ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : (
            <UsersTable users={users} />
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Error logs</CardTitle>
          <CardDescription>
            Unhandled exceptions, captured locally (also sent to Sentry independently, if
            configured).
          </CardDescription>
        </CardHeader>
        <CardContent>
          {errorLogsLoading || !errorLogs ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : (
            <ErrorLogsTable entries={errorLogs} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
