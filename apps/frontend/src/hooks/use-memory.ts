import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { MemoryRead } from "@/types/api";

export function useRecentMemories() {
  return useQuery({
    queryKey: ["memory"] as const,
    queryFn: () => apiFetch<MemoryRead[]>("/memory"),
  });
}
