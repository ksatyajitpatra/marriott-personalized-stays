"use client";

import { create } from "zustand";
import { api } from "./api";
import type { GuestSummary } from "./types";

interface AuthState {
  guest: GuestSummary | null;
  loading: boolean;
  hydrated: boolean;
  hydrate: () => Promise<void>;
  signIn: (guestId: string) => Promise<void>;
  signOut: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  guest: null,
  loading: false,
  hydrated: false,

  hydrate: async () => {
    set({ loading: true });
    try {
      const session = await api.auth.me();
      set({ guest: session.guest, hydrated: true });
    } catch {
      set({ guest: null, hydrated: true });
    } finally {
      set({ loading: false });
    }
  },

  signIn: async (guestId: string) => {
    set({ loading: true });
    try {
      const session = await api.auth.login(guestId);
      set({ guest: session.guest, hydrated: true });
    } finally {
      set({ loading: false });
    }
  },

  signOut: async () => {
    set({ loading: true });
    try {
      await api.auth.logout();
    } finally {
      set({ guest: null, loading: false });
    }
  },
}));
