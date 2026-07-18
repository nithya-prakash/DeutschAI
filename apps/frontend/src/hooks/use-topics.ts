import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { TopicRead, TopicStatus } from "@/types/api";

export const topicsKeys = {
  list: ["topics"] as const,
};

export function useTopics() {
  return useQuery({
    queryKey: topicsKeys.list,
    queryFn: () => apiFetch<TopicRead[]>("/topics"),
  });
}

export function useUpdateTopicProgress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: TopicStatus }) =>
      apiFetch<TopicRead>(`/topics/${id}/progress`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: topicsKeys.list }),
  });
}
