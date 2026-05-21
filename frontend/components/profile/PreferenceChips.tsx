"use client";

import { cn } from "@/lib/utils";

interface PreferenceChipsProps {
  label: string;
  description?: string;
  options: ReadonlyArray<{ id: string; label: string }>;
  selected: string[];
  onChange: (next: string[]) => void;
  disabled?: boolean;
}

export function PreferenceChips({
  label,
  description,
  options,
  selected,
  onChange,
  disabled = false,
}: PreferenceChipsProps): React.ReactElement {
  function toggle(id: string): void {
    if (disabled) return;
    if (selected.includes(id)) {
      onChange(selected.filter((s) => s !== id));
    } else {
      onChange([...selected, id]);
    }
  }

  return (
    <div>
      <p className="text-[13px] font-medium text-[var(--color-bonvoy-ink)] mb-1">
        {label}
      </p>
      {description && (
        <p className="text-[12px] text-[var(--color-bonvoy-muted)] mb-3">
          {description}
        </p>
      )}
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const active = selected.includes(opt.id);
          return (
            <button
              key={opt.id}
              type="button"
              disabled={disabled}
              onClick={() => toggle(opt.id)}
              className={cn(
                "px-3 py-1.5 rounded-full text-[12px] border transition-colors",
                active
                  ? "bg-[var(--color-bonvoy-ink)] text-white border-[var(--color-bonvoy-ink)]"
                  : "bg-white text-[var(--color-bonvoy-ink)] border-[var(--color-bonvoy-rule)] hover:border-[var(--color-bonvoy-ink)]",
                disabled && "opacity-60 cursor-not-allowed",
              )}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
