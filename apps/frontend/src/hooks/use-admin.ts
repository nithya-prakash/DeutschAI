import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type {
  ErrorLogEntryRead,
  LLMUsageSummary,
  SessionActivity,
  SystemHealth,
  UserRead,
} from "@/types/api";

export const adminKeys = {
  users: ["admin", "users"] as const,
  systemHealth: ["admin", "system-health"] as const,
  llmUsage: ["admin", "llm-usage"] as const,
  sessionActivity: ["admin", "session-activity"] as const,
  errorLogs: ["admin", "error-logs"] as const,
};

export function useAdminUsers() {
  return useQuery({
    queryKey: adminKeys.users,
    queryFn: () => apiFetch<UserRead[]>("/admin/users"),
  });
}

export function useAdminSystemHealth() {
  return useQuery({
    queryKey: adminKeys.systemHealth,
    queryFn: () => apiFetch<SystemHealth>("/admin/system-health"),
  });
}

export function useAdminLLMUsage() {
  return useQuery({
    queryKey: adminKeys.llmUsage,
    queryFn: () => apiFetch<LLMUsageSummary>("/admin/llm-usage"),
  });
}

export function useAdminSessionActivity() {
  return useQuery({
    queryKey: adminKeys.sessionActivity,
    queryFn: () => apiFetch<SessionActivity>("/admin/session-activity"),
  });
}

export function useAdminErrorLogs() {
  return useQuery({
    queryKey: adminKeys.errorLogs,
    queryFn: () => apiFetch<ErrorLogEntryRead[]>("/admin/error-logs"),
  });
}
