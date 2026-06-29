export type FuelType =
    | "petrol"
    | "diesel"
    | "hybrid"
    | "phev"
    | "electric"
    | "lpg";

export type Gearbox = "manual" | "automatic";

export type Confidence = "high" | "medium" | "low";

export interface Brand {
    id: number;
    name: string;
    slug: string;
}

export interface CarModel {
    id: number;
    name: string;
    slug: string;
    listings_count: number;
}

export interface PredictRequest {
    model_id: number;
    year: number;
    mileage_km: number;
    fuel_type?: FuelType;
    gearbox?: Gearbox;
    engine_capacity_cm3?: number;
    engine_power_hp?: number;
}

export interface PriceBucket {
    bucket: string;
    count: number;
}

export interface SimilarListing {
    id: number;
    year: number | null;
    mileage_km: number | null;
    price_pln: number | null;
    fuel_type: string | null;
    gearbox: string | null;
    city: string | null;
    url: string | null;
}

export interface PredictResponse {
    predicted_price_pln: number;
    price_range: { min: number; max: number };
    confidence: Confidence;
    comparables_count: number;
    price_distribution: PriceBucket[];
    similar_listings: SimilarListing[];
}