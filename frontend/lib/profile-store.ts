"use client";

import { create } from "zustand";
import { api } from "./api";
import type { GuestProfile } from "./types";

const DEFAULT_RADIUS = 10;

export type PreferenceUpdate = Partial<
  Pick<
    GuestProfile["preferences"],
    "dietary" | "interests" | "pet_service_categories" | "pet_service_radius_miles"
  >
>;

interface ProfileState {
  profile: GuestProfile | null;
  radiusMiles: number;
  loading: boolean;
  saving: boolean;
  loadProfile: () => Promise<void>;
  setRadiusMiles: (miles: number) => Promise<void>;
  updatePreferences: (updates: PreferenceUpdate) => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set, get) => ({
  profile: null,
  radiusMiles: DEFAULT_RADIUS,
  loading: false,
  saving: false,

  loadProfile: async () => {
    set({ loading: true });
    try {
      const profile = await api.auth.profile();
      const radius =
        profile.preferences.pet_service_radius_miles ?? DEFAULT_RADIUS;
      set({ profile, radiusMiles: radius });
    } catch {
      set({ profile: null, radiusMiles: DEFAULT_RADIUS });
    } finally {
      set({ loading: false });
    }
  },

  updatePreferences: async (updates: PreferenceUpdate) => {
    set({ saving: true });
    try {
      const prefs = await api.auth.updatePreferences(updates);
      const profile = get().profile;
      if (profile) {
        set({
          profile: {
            ...profile,
            preferences: { ...profile.preferences, ...prefs },
          },
          radiusMiles: prefs.pet_service_radius_miles ?? get().radiusMiles,
        });
      }
    } finally {
      set({ saving: false });
    }
  },

  setRadiusMiles: async (miles: number) => {
    const clamped = Math.min(50, Math.max(1, miles));
    set({ radiusMiles: clamped });
    await get().updatePreferences({ pet_service_radius_miles: clamped });
  },
}));
