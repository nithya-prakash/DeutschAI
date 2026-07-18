import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import type { UserRead } from "@/types/api";

export const userKeys = { me: ["users", "me"] as const };

export function useCurrentUser() {
  const setUser = useAuthStore((s) => s.setUser);
  return useQuery({
    queryKey: userKeys.me,
    queryFn: async () => {
      const user = await apiFetch<UserRead>("/users/me");
      setUser(user);
      return user;
    },
  });
}

interface UpdateProfileInput {
  full_name?: string;
  target_language?: string;
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: (input: UpdateProfileInput) =>
      apiFetch<UserRead>("/users/me", { method: "PATCH", body: JSON.stringify(input) }),
    onSuccess: (user) => {
      setUser(user);
      queryClient.invalidateQueries({ queryKey: userKeys.me });
    },
  });
}
