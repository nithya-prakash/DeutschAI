import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { VocabularyItemCreate, VocabularyItemRead } from "@/types/api";

export const vocabularyKeys = {
  list: ["vocabulary"] as const,
};

export function useVocabulary() {
  return useQuery({
    queryKey: vocabularyKeys.list,
    queryFn: () => apiFetch<VocabularyItemRead[]>("/vocabulary"),
  });
}

export function useAddWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: VocabularyItemCreate) =>
      apiFetch<VocabularyItemRead>("/vocabulary", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: vocabularyKeys.list }),
  });
}

export function useReviewWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, quality }: { id: string; quality: number }) =>
      apiFetch<VocabularyItemRead>(`/vocabulary/${id}/review`, {
        method: "POST",
        body: JSON.stringify({ quality }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: vocabularyKeys.list }),
  });
}

export function useDeleteWord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => apiFetch<void>(`/vocabulary/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: vocabularyKeys.list }),
  });
}
