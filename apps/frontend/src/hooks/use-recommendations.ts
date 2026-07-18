import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import type { RecommendationResult } from "@/types/api";

export const recommendationKeys = {
  all: ["recommendations"] as const,
};

export function useRecommendations() {
  return useQuery({
    queryKey: recommendationKeys.all,
    queryFn: () => apiFetch<RecommendationResult>("/recommendations"),
  });
}
