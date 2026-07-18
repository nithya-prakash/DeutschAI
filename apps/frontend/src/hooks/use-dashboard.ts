import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { DashboardSummary, StudySessionCreate, StudySessionRead } from "@/types/api";

export const dashboardKeys = {
  summary: ["dashboard", "summary"] as const,
};

export function useDashboardSummary() {
  return useQuery({
    queryKey: dashboardKeys.summary,
    queryFn: () => apiFetch<DashboardSummary>("/dashboard/summary"),
  });
}

export function useLogStudySession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: StudySessionCreate) =>
      apiFetch<StudySessionRead>("/dashboard/study-sessions", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dashboardKeys.summary });
    },
  });
}
