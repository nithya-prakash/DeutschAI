"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/stores/auth-store";
import { useRequireAuth } from "./use-require-auth";

/** Builds on useRequireAuth(): also redirects to /dashboard if the current
 * user isn't a superuser — the frontend-side half of the admin gate (the
 * backend's get_current_superuser dependency is the real enforcement). */
export function useRequireSuperuser() {
  const router = useRouter();
  const { isReady } = useRequireAuth();
  const user = useAuthStore((s) => s.user);

  React.useEffect(() => {
    if (isReady && user && !user.is_superuser) {
      router.replace("/dashboard");
    }
  }, [isReady, user, router]);

  return { isReady: isReady && !!user?.is_superuser };
}
