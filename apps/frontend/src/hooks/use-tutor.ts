import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { AskTutorRequest, ConversationRead, ConversationSummary, TutorAnswer } from "@/types/api";

export const tutorKeys = {
  conversations: ["tutor", "conversations"] as const,
  conversation: (id: string) => ["tutor", "conversations", id] as const,
};

export function useConversations() {
  return useQuery({
    queryKey: tutorKeys.conversations,
    queryFn: () => apiFetch<ConversationSummary[]>("/tutor/conversations"),
  });
}

export function useConversation(conversationId: string | null) {
  return useQuery({
    queryKey: conversationId ? tutorKeys.conversation(conversationId) : ["tutor", "conversation", "none"],
    queryFn: () => apiFetch<ConversationRead>(`/tutor/conversations/${conversationId}`),
    enabled: !!conversationId,
  });
}

export function useAskTutor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: AskTutorRequest) =>
      apiFetch<TutorAnswer>("/tutor/ask", { method: "POST", body: JSON.stringify(input) }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: tutorKeys.conversations });
      queryClient.invalidateQueries({ queryKey: tutorKeys.conversation(data.conversation_id) });
    },
  });
}
