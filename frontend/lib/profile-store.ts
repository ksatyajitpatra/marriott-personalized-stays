"use client";

import { create } from "zustand";
import { api } from "./api";
import type { GuestProfile } from "./types";

const DEFAULT_RADIUS = 10;

interface ProfileState {
  profile: GuestProfile | null;
  radiusMiles: number;
  loading: boolean;
  loadProfile: () => Promise<void>;
  setRadiusMiles: (miles: number) => Promise<void>;
}

export const useProfileStore = create<ProfileState>((set, get) => ({
  profile: null,
  radiusMiles: DEFAULT_RADIUS,
  loading: false,

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

  setRadiusMiles: async (miles: number) => {
    const clamped = Math.min(50, Math.max(1, miles));
    set({ radiusMiles: clamped });
    try {
      const prefs = await api.auth.updatePreferences({
        pet_service_radius_miles: clamped,
      });
      const profile = get().profile;
      if (profile) {
        set({
          profile: {
            ...profile,
            preferences: { ...profile.preferences, ...prefs },
          },
          radiusMiles: prefs.pet_service_radius_miles ?? clamped,
        });
      }
    } catch {
      /* keep optimistic local value */
    }
  },
}));
