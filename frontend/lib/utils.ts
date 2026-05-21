/**
 * Common Tailwind-class helpers + small format utilities used across pages.
 */

import { clsx, type ClassValue } from "clsx";

export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export function formatUsd(n: number): string {
  return n.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatShortDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

export function ecoColorVar(color: "green" | "yellow" | "red"): string {
  return `var(--color-eco-${color})`;
}

/** Stable Unsplash image for a city, used as hotel hero fallback. */
export function cityHeroImage(city: string): string {
  const map: Record<string, string> = {
    "New York":
      "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1800&q=80",
    Washington:
      "https://images.unsplash.com/photo-1617469767053-d3b523a0b982?auto=format&fit=crop&w=1800&q=80",
    Chicago:
      "https://images.unsplash.com/photo-1494522855154-9297ac14b55f?auto=format&fit=crop&w=1800&q=80",
    Miami:
      "https://images.unsplash.com/photo-1535498730771-e735b998cd64?auto=format&fit=crop&w=1800&q=80",
  };
  return (
    map[city] ??
    "https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&w=1800&q=80"
  );
}
