import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { QuizAttemptResult, QuizQuestionRead } from "@/types/api";

export function useQuizQuestion(topicId: string | null) {
  return useQuery({
    queryKey: ["quiz", "question", topicId] as const,
    queryFn: () => apiFetch<QuizQuestionRead>(`/quizzes/topics/${topicId}/question`),
    enabled: !!topicId,
    staleTime: 0,
  });
}

export function useSubmitAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { question_id: string; selected_option_index: number }) =>
      apiFetch<QuizAttemptResult>("/quizzes/attempts", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memory"] });
    },
  });
}
