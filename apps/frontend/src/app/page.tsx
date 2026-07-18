"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { useAuthStore } from "@/stores/auth-store";

export default function RootPage() {
  const router = useRouter();
  const accessToken = useAuthStore((s) => s.accessToken);

  React.useEffect(() => {
    router.replace(accessToken ? "/dashboard" : "/login");
  }, [accessToken, router]);

  return null;
}
