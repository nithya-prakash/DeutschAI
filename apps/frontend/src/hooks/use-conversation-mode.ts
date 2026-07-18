import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, apiFetchBlob } from "@/lib/api-client";
import type {
  SpeechConversationRead,
  SpeechConversationSummary,
  SubmitTurnResponse,
} from "@/types/api";

export const speechKeys = {
  conversations: ["speech", "conversations"] as const,
  conversation: (id: string) => ["speech", "conversations", id] as const,
};

export function useSpeechConversations() {
  return useQuery({
    queryKey: speechKeys.conversations,
    queryFn: () => apiFetch<SpeechConversationSummary[]>("/speech/conversations"),
  });
}

export function useSpeechConversation(conversationId: string | null) {
  return useQuery({
    queryKey: conversationId ? speechKeys.conversation(conversationId) : ["speech", "conversation", "none"],
    queryFn: () => apiFetch<SpeechConversationRead>(`/speech/conversations/${conversationId}`),
    enabled: !!conversationId,
  });
}

export function useSubmitTurn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ audio, conversationId }: { audio: Blob; conversationId: string | null }) => {
      const formData = new FormData();
      formData.append("audio", audio, "clip.webm");
      if (conversationId) {
        formData.append("conversation_id", conversationId);
      }
      return apiFetch<SubmitTurnResponse>("/speech/turns", { method: "POST", body: formData });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: speechKeys.conversations });
      queryClient.invalidateQueries({ queryKey: speechKeys.conversation(data.conversation_id) });
    },
  });
}

/** Fetches a turn's audio with the same bearer auth as everything else
 * (rather than a public MinIO URL) and exposes it as an object URL for
 * `<audio src>` playback, revoked on unmount/turn change. */
export function useTurnAudioUrl(turnId: string | null) {
  const [url, setUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!turnId) {
      setUrl(null);
      return;
    }
    let objectUrl: string | null = null;
    let cancelled = false;

    apiFetchBlob(`/speech/turns/${turnId}/audio`).then((blob) => {
      if (cancelled) return;
      objectUrl = URL.createObjectURL(blob);
      setUrl(objectUrl);
    });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [turnId]);

  return url;
}
