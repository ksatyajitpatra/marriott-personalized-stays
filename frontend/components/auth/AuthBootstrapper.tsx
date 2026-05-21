"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/lib/auth-store";

/**
 * Hydrates the persona session on first render. Mounted in the root layout
 * so any page can read `useAuthStore()` immediately after first paint.
 */
export function AuthBootstrapper(): null {
  const hydrate = useAuthStore((s) => s.hydrate);
  const hydrated = useAuthStore((s) => s.hydrated);

  useEffect(() => {
    if (!hydrated) void hydrate();
  }, [hydrate, hydrated]);

  return null;
}
