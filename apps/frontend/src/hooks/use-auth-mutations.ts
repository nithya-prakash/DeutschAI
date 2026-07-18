import { useMutation } from "@tanstack/react-query";

import { apiFetch } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import type { TokenResponse, UserRead } from "@/types/api";

interface RegisterInput {
  email: string;
  password: string;
  full_name: string;
}

interface LoginInput {
  email: string;
  password: string;
}

export function useRegister() {
  return useMutation({
    mutationFn: (input: RegisterInput) =>
      apiFetch<UserRead>("/auth/register", {
        method: "POST",
        body: JSON.stringify(input),
        auth: false,
      }),
  });
}

export function useLogin() {
  const setTokens = useAuthStore((s) => s.setTokens);
  const setUser = useAuthStore((s) => s.setUser);

  return useMutation({
    mutationFn: async (input: LoginInput) => {
      const tokens = await apiFetch<TokenResponse>("/auth/login", {
        method: "POST",
        body: JSON.stringify(input),
        auth: false,
      });
      setTokens(tokens.access_token, tokens.refresh_token);

      const user = await apiFetch<UserRead>("/users/me");
      setUser(user);
      return user;
    },
  });
}
