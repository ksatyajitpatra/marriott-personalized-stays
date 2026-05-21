import { cn } from "@/lib/utils";

interface EcoScoreRingProps {
  score: number;
  color: "green" | "yellow" | "red";
  size?: number;
  label?: string;
  className?: string;
}

/**
 * Circular SVG eco rating ring (PRD 5.1). Stroke color comes from the
 * theme tokens: green / yellow / red.
 */
export function EcoScoreRing({
  score,
  color,
  size = 56,
  label,
  className,
}: EcoScoreRingProps): React.ReactElement {
  const stroke = `var(--color-eco-${color})`;
  const r = (size - 6) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(1, score / 10));
  const offset = c * (1 - pct);

  return (
    <div
      className={cn("inline-flex items-center gap-2", className)}
      title={`Eco rating ${score.toFixed(1)} of 10`}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="block"
        aria-hidden
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke="rgba(0,0,0,0.08)"
          strokeWidth={4}
          fill="white"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={stroke}
          strokeWidth={4}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={c}
          strokeDashoffset={offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ transition: "stroke-dashoffset 600ms ease" }}
        />
        <text
          x="50%"
          y="50%"
          dominantBaseline="middle"
          textAnchor="middle"
          fill="var(--color-bonvoy-ink)"
          style={{ fontSize: size * 0.32, fontWeight: 600 }}
        >
          {score.toFixed(1)}
        </text>
      </svg>
      {label && (
        <span className="text-[12px] text-[var(--color-bonvoy-muted)] uppercase tracking-[0.14em]">
          {label}
        </span>
      )}
    </div>
  );
}
