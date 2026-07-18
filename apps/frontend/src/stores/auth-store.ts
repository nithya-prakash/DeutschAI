import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { UserRead } from "@/types/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserRead | null;
  setTokens: (accessToken: string, refreshToken: string) => void;
  setUser: (user: UserRead) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      setUser: (user) => set({ user }),
      logout: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    { name: "deutschai-auth" }
  )
);
