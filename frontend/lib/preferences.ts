/** Guest preference options — keep in sync with backend/app/models/preferences.py */

export const DIETARY_OPTIONS = [
  { id: "vegetarian", label: "Vegetarian" },
  { id: "vegan", label: "Vegan" },
  { id: "halal", label: "Halal" },
  { id: "kosher", label: "Kosher" },
  { id: "gluten_free", label: "Gluten-free" },
  { id: "nut_allergy", label: "Nut allergy" },
] as const;

export const INTEREST_OPTIONS = [
  { id: "culture", label: "Culture" },
  { id: "food", label: "Food" },
  { id: "outdoor", label: "Outdoor" },
  { id: "nightlife", label: "Nightlife" },
  { id: "sustainability", label: "Sustainability" },
  { id: "wellness", label: "Wellness" },
] as const;

export const PET_SERVICE_CATEGORY_OPTIONS = [
  { id: "dog_walker", label: "Dog walking & sitting" },
  { id: "mobile_grooming", label: "Mobile grooming" },
] as const;

export type DietaryId = (typeof DIETARY_OPTIONS)[number]["id"];
export type InterestId = (typeof INTEREST_OPTIONS)[number]["id"];
export type PetServiceCategoryId = (typeof PET_SERVICE_CATEGORY_OPTIONS)[number]["id"];
