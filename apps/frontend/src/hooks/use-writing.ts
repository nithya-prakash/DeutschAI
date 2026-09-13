import { useMutation, useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { WritingPromptRead, WritingSubmissionResult } from "@/types/api";

export function useWritingPrompt() {
  return useQuery({
    queryKey: ["writing", "prompt"] as const,
    queryFn: () => apiFetch<WritingPromptRead>("/writing/prompts/random"),
    staleTime: 0,
  });
}

export function useSubmitWriting() {
  return useMutation({
    mutationFn: (input: { prompt_id: string; submitted_text: string }) =>
      apiFetch<WritingSubmissionResult>("/writing/submissions", {
        method: "POST",
        body: JSON.stringify(input),
      }),
  });
}
