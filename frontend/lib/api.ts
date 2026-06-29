import type { Brand, CarModel, PredictRequest, PredictResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });

    if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: "Błąd serwera" }));
        throw new Error(error.detail ?? `HTTP ${res.status}`);
    }

    return res.json() as Promise<T>;
}

export async function getBrands(): Promise<Brand[]> {
    return apiFetch<Brand[]>("/brands");
}

export async function getModels(brandId: number): Promise<CarModel[]> {
    return apiFetch<CarModel[]>(`/brands/${brandId}/models`);
}

export async function predict(body: PredictRequest): Promise<PredictResponse> {
    return apiFetch<PredictResponse>("/predict", {
        method: "POST",
        body: JSON.stringify(body),
    });
}