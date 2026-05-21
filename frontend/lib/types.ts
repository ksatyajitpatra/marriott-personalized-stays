/**
 * Shared API types — mirror the FastAPI Pydantic models in
 * backend/app/models. Keep these in sync when the backend changes.
 */

export type EcoColor = "green" | "yellow" | "red";

export interface GuestSummary {
  id: string;
  name: string;
  email: string;
  bonvoy_id: string;
  tier: string;
  tier_color: string;
  points: number;
}

export interface SessionResponse {
  authenticated: boolean;
  guest: GuestSummary | null;
}

export interface GuestProfile extends GuestSummary {
  badges: string[];
  preferences: {
    dietary: string[];
    interests: string[];
    accessibility: string[];
    arrival_brief_enabled: boolean;
    eco_nudges_enabled: boolean;
    local_partners_enabled: boolean;
    preference_learning_enabled: boolean;
    pet_service_radius_miles: number;
    pet_service_categories: string[];
  };
  pets: Array<{
    id: string;
    name: string;
    species: string;
    breed: string;
    weight_kg: number;
    photo_url: string | null;
  }>;
  language: string;
}

export interface HotelListItem {
  id: string;
  name: string;
  brand: string;
  city: string;
  state: string;
  address: string;
  lat: number;
  lng: number;
  image_url: string;
  price_per_night: number;
  rating: number;
  pet_friendly: boolean;
  eco_score: number;
  eco_color: EcoColor;
  tagline: string;
}

export interface HotelContent {
  tagline: string;
  highlights: string[];
  editorial: string;
  room_types: string[];
  generated_by: "mock_llm" | "litellm";
}

export interface HotelDetail {
  id: string;
  name: string;
  brand: string;
  city: string;
  state: string;
  country: string;
  address: string;
  lat: number;
  lng: number;
  image_url: string;
  price_per_night: number;
  rating: number;
  pet_friendly: boolean;
  pet_max_weight_kg: number | null;
  pet_fee_usd: number | null;
  pet_note: string | null;
  eco_score: number;
  eco_color: EcoColor;
  community_events: Array<{
    name: string;
    time: string;
    location: string;
    type: string;
  }>;
  content: HotelContent;
}

export interface EcoSubScore {
  key: string;
  label: string;
  score: number;
  raw_value: string;
  weight_pct: number;
  data_source: string;
}

export interface EcoScoreResponse {
  hotel_id: string;
  total_score: number;
  color: EcoColor;
  green_points_bonus: number;
  green_points_multiplier: number;
  sub_scores: EcoSubScore[];
  data_as_of: string;
  data_source: string;
}

export interface PartnerResponse {
  id: string;
  hotel_id: string;
  name: string;
  category: string;
  service_model: "fixed_location" | "mobile";
  bookable: boolean;
  lat: number;
  lng: number;
  address: string;
  phone: string | null;
  hours: string | null;
  rating: number;
  is_marriott_partner: boolean;
  pet_relevant: boolean;
  distance_km: number;
  distance_miles: number;
  note: string | null;
  dietary_tags: string[];
  service_area_miles: number | null;
  mobile_service_note: string | null;
}

export interface PetServiceRecommendationItem {
  partner_id: string;
  partner_name: string;
  category: string;
  service_model: "fixed_location" | "mobile";
  distance_miles: number;
  rating: number;
  bookable: boolean;
  mobile_service_note: string | null;
  rationale: string;
  suggested_time: string | null;
  priority: number;
}

export interface PetServiceRecommendationsResponse {
  reservation_id: string;
  generated_at: string;
  generated_by: "mock_llm" | "litellm";
  radius_miles: number;
  summary: string;
  recommendations: PetServiceRecommendationItem[];
}

export interface PetServiceBooking {
  id: string;
  partner_id: string;
  partner_name: string;
  category: string;
  service_model: string;
  service_date: string;
  service_time: string;
  notes: string;
  status: string;
}

export interface ReservationResponse {
  id: string;
  guest_id: string;
  hotel_id: string;
  hotel_name: string;
  hotel_city: string;
  hotel_image_url: string;
  check_in: string;
  check_out: string;
  nights: number;
  room_type: string;
  confirmation_number: string;
  status: "pending_payment" | "upcoming" | "in_stay" | "completed";
  has_pet: boolean;
  pet_id: string | null;
  pet_fee_charged: number | null;
  total_usd: number;
  payment_status: "unpaid" | "paid";
  pet_service_bookings: PetServiceBooking[];
}

export interface BriefEvent {
  name: string;
  date: string;
  type: string;
  why_youll_love_it: string;
}

export interface BriefDining {
  name: string;
  cuisine: string;
  dietary_match: string;
  note: string;
}

export interface WeatherDay {
  date: string;
  high_c: number;
  low_c: number;
  summary: string;
  icon: "sun" | "cloud" | "rain" | "snow" | "partly";
}

export interface ArrivalBriefResponse {
  stay_id: string;
  guest_id: string;
  hotel: string;
  city: string;
  check_in: string;
  check_out: string;
  generated_at: string;
  generated_by: "seed" | "mock_llm" | "litellm";
  greeting: string;
  weather_summary: string;
  weather_forecast: WeatherDay[];
  packing_tips: string[];
  events: BriefEvent[];
  dining: BriefDining[];
  transit: string;
  property_note: string;
  eco_note: string | null;
}
