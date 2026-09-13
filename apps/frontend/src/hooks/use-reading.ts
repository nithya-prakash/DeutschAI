import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { ReadingAttemptResult, ReadingPassageRead } from "@/types/api";

export function useReadingPassage() {
  return useQuery({
    queryKey: ["reading", "passage"] as const,
    queryFn: () => apiFetch<ReadingPassageRead>("/reading/passages/random"),
    staleTime: 0,
  });
}

export function useSubmitReadingAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { passage_id: string; selected_option_index: number }) =>
      apiFetch<ReadingAttemptResult>("/reading/attempts", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memory"] });
    },
  });
}
