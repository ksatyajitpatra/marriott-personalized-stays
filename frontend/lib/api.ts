/**
 * Typed FastAPI client. All calls send credentials so the persona
 * session cookie is preserved cross-request. Throws ApiError on non-2xx.
 */

import type {
  ArrivalBriefResponse,
  BadgeShelfResponse,
  EcoScoreResponse,
  GuestProfile,
  GuestSummary,
  HotelDetail,
  HotelListItem,
  PartnerResponse,
  PetServiceBooking,
  PetServiceRecommendationsResponse,
  ReservationResponse,
  SessionResponse,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  payload: unknown;

  constructor(status: number, message: string, payload: unknown) {
    super(message);
    this.status = status;
    this.payload = payload;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
}

function buildUrl(
  path: string,
  query?: RequestOptions["query"],
): string {
  const url = new URL(path.replace(/^\//, ""), `${API_BASE_URL}/`);
  if (query) {
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null || v === "") continue;
      url.searchParams.set(k, String(v));
    }
  }
  return url.toString();
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { body, query, headers, ...rest } = opts;
  const init: RequestInit = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(await serverCookieHeader()),
      ...(headers ?? {}),
    },
    ...rest,
  };
  if (body !== undefined) init.body = JSON.stringify(body);

  const res = await fetch(buildUrl(path, query), init);
  const text = await res.text();
  const payload = text ? safeJson(text) : null;

  if (!res.ok) {
    const detail =
      (payload && typeof payload === "object" && "detail" in payload
        ? String((payload as { detail: unknown }).detail)
        : null) ?? res.statusText;
    throw new ApiError(res.status, detail, payload);
  }
  return payload as T;
}

/**
 * On the server, forward the incoming request's cookies so persona
 * sessions survive RSC fetches. On the client this is a no-op
 * (the browser handles cookies via `credentials: "include"`).
 */
async function serverCookieHeader(): Promise<Record<string, string>> {
  if (typeof window !== "undefined") return {};
  try {
    const { cookies } = await import("next/headers");
    const all = (await cookies()).getAll();
    if (all.length === 0) return {};
    return {
      Cookie: all.map((c) => `${c.name}=${c.value}`).join("; "),
    };
  } catch {
    return {};
  }
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

/* ----------------------------- Auth ----------------------------- */

export const auth = {
  login: (guest_id: string) =>
    request<SessionResponse>("/auth/login", {
      method: "POST",
      body: { guest_id },
    }),
  logout: () => request<{ ok: boolean }>("/auth/logout", { method: "POST" }),
  me: () => request<SessionResponse>("/auth/me"),
  profile: () => request<GuestProfile>("/auth/profile"),
  updatePreferences: (payload: { pet_service_radius_miles?: number }) =>
    request<GuestProfile["preferences"]>("/auth/profile/preferences", {
      method: "PATCH",
      body: payload,
    }),
  badges: () => request<BadgeShelfResponse>("/auth/badges"),
};

/* ---------------------------- Guests ---------------------------- */

export const guests = {
  list: () => request<GuestSummary[]>("/guests"),
  get: (id: string) => request<GuestProfile>(`/guests/${id}`),
};

/* ---------------------------- Hotels ---------------------------- */

export interface HotelListQuery {
  city?: string;
  pet_friendly?: boolean;
  min_eco?: number;
  brand?: string;
}

export const hotels = {
  list: (q?: HotelListQuery) =>
    request<HotelListItem[]>("/hotels", {
      query: q as unknown as RequestOptions["query"],
    }),
  get: (id: string) => request<HotelDetail>(`/hotels/${id}`),
  ecoScore: (id: string) =>
    request<EcoScoreResponse>(`/hotels/${id}/eco-score`),
};

/* --------------------------- Partners --------------------------- */

export interface PartnerNearbyQuery {
  hotel_id: string;
  pet_only?: boolean;
  bookable_only?: boolean;
  max_miles?: number;
  category?: string;
}

export const partners = {
  nearby: (q: PartnerNearbyQuery) =>
    request<PartnerResponse[]>("/partners/nearby", {
      query: q as unknown as RequestOptions["query"],
    }),
};

/* -------------------------- Reservations ------------------------ */

export const reservations = {
  list: () => request<ReservationResponse[]>("/reservations"),
  get: (id: string) => request<ReservationResponse>(`/reservations/${id}`),
  lookup: (confirmation_number: string) =>
    request<ReservationResponse>("/reservations/lookup", {
      method: "POST",
      body: { confirmation_number },
    }),
  create: (payload: {
    hotel_id: string;
    check_in: string;
    check_out: string;
    room_type: string;
    guests: number;
    has_pet: boolean;
    pet_id?: string | null;
  }) =>
    request<ReservationResponse>("/reservations", {
      method: "POST",
      body: payload,
    }),
  pay: (id: string, payload: {
    card_number: string;
    expiry: string;
    cvv: string;
    cardholder_name: string;
  }) =>
    request<ReservationResponse>(`/reservations/${id}/payment`, {
      method: "POST",
      body: payload,
    }),
  bookPetService: (
    id: string,
    payload: {
      partner_id: string;
      service_date: string;
      service_time: string;
      notes?: string;
    },
  ) =>
    request<PetServiceBooking>(`/reservations/${id}/pet-services`, {
      method: "POST",
      body: { notes: "", ...payload },
    }),
  cancelPetService: (reservationId: string, bookingId: string) =>
    request<PetServiceBooking>(
      `/reservations/${reservationId}/pet-services/${bookingId}`,
      { method: "DELETE" },
    ),
  petServiceRecommendations: (reservationId: string) =>
    request<PetServiceRecommendationsResponse>(
      `/reservations/${reservationId}/pet-services/recommendations`,
    ),
};

/* ------------------------- Arrival Brief ------------------------ */

export const arrivalBrief = {
  get: (stayId: string) =>
    request<ArrivalBriefResponse>(`/arrival-brief/${stayId}`),
};

export const api = {
  auth,
  guests,
  hotels,
  partners,
  reservations,
  arrivalBrief,
};
