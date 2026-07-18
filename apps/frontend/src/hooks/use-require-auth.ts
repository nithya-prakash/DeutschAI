"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/stores/auth-store";

/** Redirects to /login when there's no access token. Renders children only once authenticated. */
export function useRequireAuth() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    setHydrated(true);
  }, []);

  React.useEffect(() => {
    if (hydrated && !accessToken) {
      router.replace("/login");
    }
  }, [hydrated, accessToken, router]);

  return { isReady: hydrated && !!accessToken };
}
