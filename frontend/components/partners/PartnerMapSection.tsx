"use client";

import { useEffect } from "react";
import type { HotelDetail } from "@/lib/types";
import { PartnerMap } from "@/components/partners/PartnerMap";
import { useAuthStore } from "@/lib/auth-store";
import { useProfileStore } from "@/lib/profile-store";

interface PartnerMapSectionProps {
  hotel: HotelDetail;
}

/** Hotel detail map — discovery mode with optional radius control when signed in. */
export function PartnerMapSection({
  hotel,
}: PartnerMapSectionProps): React.ReactElement {
  const guest = useAuthStore((s) => s.guest);
  const hydrated = useAuthStore((s) => s.hydrated);
  const radiusMiles = useProfileStore((s) => s.radiusMiles);
  const loadProfile = useProfileStore((s) => s.loadProfile);
  const setRadiusMiles = useProfileStore((s) => s.setRadiusMiles);

  useEffect(() => {
    if (hydrated && guest) void loadProfile();
  }, [guest, hydrated, loadProfile]);

  return (
    <PartnerMap
      hotel={hotel}
      radiusMiles={radiusMiles}
      onRadiusChange={guest ? (m) => void setRadiusMiles(m) : undefined}
    />
  );
}
