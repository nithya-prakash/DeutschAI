import * as React from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch, apiFetchBlob } from "@/lib/api-client";
import type { ListeningAttemptResult, ListeningScriptRead } from "@/types/api";

export function useListeningScript() {
  return useQuery({
    queryKey: ["listening", "script"] as const,
    queryFn: () => apiFetch<ListeningScriptRead>("/listening/scripts/random"),
    staleTime: 0,
  });
}

export function useSubmitListeningAttempt() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: { script_id: string; selected_option_index: number }) =>
      apiFetch<ListeningAttemptResult>("/listening/attempts", {
        method: "POST",
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["memory"] });
    },
  });
}

/** Mirrors use-conversation-mode.ts's useTurnAudioUrl — fetches audio with
 * the same bearer auth as everything else and exposes it as an object URL
 * for `<audio src>` playback, revoked on unmount/script change. */
export function useScriptAudioUrl(scriptId: string | null) {
  const [url, setUrl] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!scriptId) {
      setUrl(null);
      return;
    }
    let objectUrl: string | null = null;
    let cancelled = false;

    apiFetchBlob(`/listening/scripts/${scriptId}/audio`).then((blob) => {
      if (cancelled) return;
      objectUrl = URL.createObjectURL(blob);
      setUrl(objectUrl);
    });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [scriptId]);

  return url;
}
