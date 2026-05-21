import { Truck } from "lucide-react";
import { cn } from "@/lib/utils";

interface MobileServiceBadgeProps {
  className?: string;
}

export function MobileServiceBadge({
  className,
}: MobileServiceBadgeProps): React.ReactElement {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full bg-[#eef6ff] text-[#0f6cbf] px-2 py-0.5 text-[10px] uppercase tracking-[0.14em] font-medium",
        className,
      )}
    >
      <Truck size={10} aria-hidden />
      Comes to you
    </span>
  );
}
