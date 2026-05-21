"use client";

import { cn } from "@/lib/utils";

interface PetServiceRadiusControlProps {
  value: number;
  onChange: (miles: number) => void;
  compact?: boolean;
  className?: string;
}

export function PetServiceRadiusControl({
  value,
  onChange,
  compact = false,
  className,
}: PetServiceRadiusControlProps): React.ReactElement {
  return (
    <div className={cn(compact ? "space-y-1" : "space-y-2", className)}>
      <div className="flex items-center justify-between gap-3">
        <label
          htmlFor="pet-service-radius"
          className={cn(
            "text-[var(--color-bonvoy-ink)]",
            compact ? "text-[12px]" : "text-[14px] font-medium",
          )}
        >
          Search within
        </label>
        <span
          className={cn(
            "tabular-nums text-[var(--color-marriott-red)] font-medium",
            compact ? "text-[12px]" : "text-[14px]",
          )}
        >
          {value} mi
        </span>
      </div>
      <input
        id="pet-service-radius"
        type="range"
        min={1}
        max={50}
        step={1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[var(--color-marriott-red)]"
        aria-valuemin={1}
        aria-valuemax={50}
        aria-valuenow={value}
      />
      {!compact && (
        <p className="text-[12px] text-[var(--color-bonvoy-muted)]">
          Bookable pet services are shown within this radius from your hotel.
          Default is 10 miles.
        </p>
      )}
    </div>
  );
}
