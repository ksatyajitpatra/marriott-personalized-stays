"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { PawPrint } from "lucide-react";
import { useAuthStore } from "@/lib/auth-store";
import { useProfileStore } from "@/lib/profile-store";
import { PetServiceRadiusControl } from "@/components/pet/PetServiceRadiusControl";
import { BadgeShelf } from "@/components/eco/BadgeShelf";

export default function ProfilePage(): React.ReactElement {
  const router = useRouter();
  const guest = useAuthStore((s) => s.guest);
  const hydrated = useAuthStore((s) => s.hydrated);
  const profile = useProfileStore((s) => s.profile);
  const radiusMiles = useProfileStore((s) => s.radiusMiles);
  const loadProfile = useProfileStore((s) => s.loadProfile);
  const setRadiusMiles = useProfileStore((s) => s.setRadiusMiles);
  const loading = useProfileStore((s) => s.loading);

  useEffect(() => {
    if (!hydrated) return;
    if (!guest) {
      router.replace("/sign-in?next=/profile");
      return;
    }
    void loadProfile();
  }, [guest, hydrated, loadProfile, router]);

  if (!hydrated || !guest) {
    return (
      <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)] py-10 px-6">
        <div className="mx-auto max-w-[720px] h-64 bg-white rounded-lg border animate-pulse" />
      </div>
    );
  }

  return (
    <div className="bg-[var(--color-bonvoy-mist)] min-h-[calc(100vh-4rem)] py-10 px-6">
      <div className="mx-auto max-w-[720px] space-y-6">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--color-marriott-red)] mb-1">
            Bonvoy profile
          </p>
          <h1 className="heading-display text-3xl text-[var(--color-bonvoy-ink)]">
            {guest.name}
          </h1>
          <p className="text-[14px] text-[var(--color-bonvoy-muted)] mt-1">
            {guest.tier} · {guest.points.toLocaleString()} points
          </p>
        </div>

        <BadgeShelf />

        <section className="bg-white border border-[var(--color-bonvoy-rule)] rounded-lg p-6">
          <div className="flex items-center gap-2 mb-4">
            <PawPrint size={16} className="text-[var(--color-marriott-red)]" />
            <h2 className="text-[18px] font-medium text-[var(--color-bonvoy-ink)]">
              Pet preferences
            </h2>
          </div>

          {loading && !profile ? (
            <div className="h-24 animate-pulse bg-[var(--color-bonvoy-mist)] rounded-md" />
          ) : (
            <>
              <PetServiceRadiusControl
                value={radiusMiles}
                onChange={(m) => void setRadiusMiles(m)}
              />

              {profile && profile.pets.length > 0 ? (
                <ul className="mt-6 space-y-2 border-t border-[var(--color-bonvoy-rule)] pt-4">
                  {profile.pets.map((pet) => (
                    <li
                      key={pet.id}
                      className="text-[14px] text-[var(--color-bonvoy-ink)]"
                    >
                      <span className="font-medium">{pet.name}</span>
                      <span className="text-[var(--color-bonvoy-muted)]">
                        {" "}
                        · {pet.breed} ({pet.weight_kg} kg)
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-[13px] text-[var(--color-bonvoy-muted)]">
                  No pets on file. Add a pet when booking a pet-friendly hotel.
                </p>
              )}
            </>
          )}
        </section>

        <p className="text-[13px] text-[var(--color-bonvoy-muted)]">
          Book mobile grooming and other pet services from{" "}
          <Link href="/trips" className="text-[var(--color-marriott-red)] hover:underline">
            My Trips
          </Link>{" "}
          when your reservation includes a pet.
        </p>
      </div>
    </div>
  );
}
