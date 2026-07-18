import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { DailyPlan } from "@/types/api";

export function useTodayPlan(availableMinutes: number) {
  return useQuery({
    queryKey: ["planner", "today", availableMinutes] as const,
    queryFn: () => apiFetch<DailyPlan>(`/planner/today?available_minutes=${availableMinutes}`),
  });
}
