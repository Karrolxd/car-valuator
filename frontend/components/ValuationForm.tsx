"use client";

import { useState } from "react";
import { getModels, predict } from "@/lib/api";
import type {
    Brand,
    CarModel,
    FuelType,
    Gearbox,
    PredictResponse,
} from "@/lib/types";
import { PriceResult } from "@/components/PriceResult";

const FUEL_TYPES: { value: FuelType; label: string }[] = [
    { value: "petrol", label: "Benzyna" },
    { value: "diesel", label: "Diesel" },
    { value: "hybrid", label: "Hybryda" },
    { value: "phev", label: "Hybryda plug-in" },
    { value: "electric", label: "Elektryczny" },
    { value: "lpg", label: "LPG" },
];

const GEARBOXES: { value: Gearbox; label: string }[] = [
    { value: "manual", label: "Manualna" },
    { value: "automatic", label: "Automatyczna" },
];

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: CURRENT_YEAR - 1989 }, (_, i) => CURRENT_YEAR - i);

interface Props {
    brands: Brand[];
}

export function ValuationForm({ brands }: Props) {
    const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
    const [models, setModels] = useState<CarModel[]>([]);
    const [modelsLoading, setModelsLoading] = useState(false);
    const [selectedModelId, setSelectedModelId] = useState<number | null>(null);
    const [year, setYear] = useState<string>("");
    const [mileage, setMileage] = useState<string>("");
    const [fuelType, setFuelType] = useState<FuelType | "">("");
    const [gearbox, setGearbox] = useState<Gearbox | "">("");
    const [engineCapacity, setEngineCapacity] = useState<string>("");
    const [enginePower, setEnginePower] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    async function handleBrandChange(brandId: number) {
        const brand = brands.find((b) => b.id === brandId) ?? null;
        setSelectedBrand(brand);
        setSelectedModelId(null);
        setModels([]);
        setResult(null);
        setError(null);

        if (!brand) return;

        setModelsLoading(true);
        try {
            const data = await getModels(brandId);
            setModels(data);
        } catch {
            setError("Nie udało się pobrać modeli");
        } finally {
            setModelsLoading(false);
        }
    }

    async function handleSubmit() {
        if (!selectedModelId || !year || !mileage) return;

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await predict({
                model_id: selectedModelId,
                year: parseInt(year),
                mileage_km: parseInt(mileage),
                fuel_type: fuelType || undefined,
                gearbox: gearbox || undefined,
                engine_capacity_cm3: engineCapacity ? parseInt(engineCapacity) : undefined,
                engine_power_hp: enginePower ? parseInt(enginePower) : undefined,
            });
            setResult(data);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Wystąpił błąd");
        } finally {
            setLoading(false);
        }
    }

    const canSubmit = !!selectedModelId && !!year && !!mileage && !loading;

    return (
        <div style={{ display: "contents" }}>
            {/* Formularz */}
            <div className="card" style={{ display: "flex", flexDirection: "column", gap: "20px" }}>

                {/* Marka */}
                <div>
                    <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                        Marka
                    </label>
                    <select
                        className="input"
                        onChange={(e) => handleBrandChange(Number(e.target.value))}
                        defaultValue=""
                    >
                        <option value="" disabled>Wybierz markę</option>
                        {brands.map((b) => (
                            <option key={b.id} value={b.id}>{b.name}</option>
                        ))}
                    </select>
                </div>

                {/* Model */}
                <div>
                    <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                        Model
                    </label>
                    <select
                        className="input"
                        disabled={!selectedBrand || modelsLoading}
                        onChange={(e) => setSelectedModelId(Number(e.target.value))}
                        defaultValue=""
                    >
                        <option value="" disabled>
                            {modelsLoading ? "Ładowanie..." : !selectedBrand ? "Najpierw wybierz markę" : "Wybierz model"}
                        </option>
                        {models.map((m) => (
                            <option key={m.id} value={m.id}>
                                {m.name} ({m.listings_count.toLocaleString("pl-PL")} ogłoszeń)
                            </option>
                        ))}
                    </select>
                </div>

                {/* Rocznik + Przebieg */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Rocznik
                        </label>
                        <select
                            className="input"
                            value={year}
                            onChange={(e) => setYear(e.target.value)}
                        >
                            <option value="" disabled>Rok</option>
                            {YEARS.map((y) => (
                                <option key={y} value={y}>{y}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Przebieg (km)
                        </label>
                        <input
                            type="number"
                            className="input"
                            placeholder="np. 95000"
                            value={mileage}
                            onChange={(e) => setMileage(e.target.value)}
                            min={0}
                            max={500000}
                        />
                    </div>
                </div>

                <hr className="divider" />

                {/* Paliwo + Skrzynia */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Paliwo <span style={{ color: "var(--muted)", fontWeight: 400 }}>(opcjonalnie)</span>
                        </label>
                        <select
                            className="input"
                            value={fuelType}
                            onChange={(e) => setFuelType(e.target.value as FuelType | "")}
                        >
                            <option value="">Dowolne</option>
                            {FUEL_TYPES.map((f) => (
                                <option key={f.value} value={f.value}>{f.label}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Skrzynia <span style={{ color: "var(--muted)", fontWeight: 400 }}>(opcjonalnie)</span>
                        </label>
                        <select
                            className="input"
                            value={gearbox}
                            onChange={(e) => setGearbox(e.target.value as Gearbox | "")}
                        >
                            <option value="">Dowolna</option>
                            {GEARBOXES.map((g) => (
                                <option key={g.value} value={g.value}>{g.label}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Pojemność + Moc */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Pojemność (cm³) <span style={{ color: "var(--muted)", fontWeight: 400 }}>(opcjonalnie)</span>
                        </label>
                        <input
                            type="number"
                            className="input"
                            placeholder="np. 1968"
                            value={engineCapacity}
                            onChange={(e) => setEngineCapacity(e.target.value)}
                            min={500}
                            max={10000}
                        />
                    </div>
                    <div>
                        <label className="label" style={{ display: "block", marginBottom: "8px" }}>
                            Moc (KM) <span style={{ color: "var(--muted)", fontWeight: 400 }}>(opcjonalnie)</span>
                        </label>
                        <input
                            type="number"
                            className="input"
                            placeholder="np. 150"
                            value={enginePower}
                            onChange={(e) => setEnginePower(e.target.value)}
                            min={40}
                            max={1000}
                        />
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div
                        style={{
                            background: "rgba(239,68,68,0.1)",
                            border: "1px solid rgba(239,68,68,0.3)",
                            borderRadius: "8px",
                            padding: "12px 16px",
                            color: "#ef4444",
                            fontSize: "0.875rem",
                        }}
                    >
                        {error}
                    </div>
                )}

                {/* Submit */}
                <button
                    className="btn-primary"
                    onClick={handleSubmit}
                    disabled={!canSubmit}
                >
                    {loading ? "Obliczam wycenę..." : "Wyceń auto"}
                </button>
            </div>

            {/* Wyniki */}
            {result && (
                <div className="animate-result">
                    <PriceResult result={result} />
                </div>
            )}

            {/* Placeholder gdy brak wyników */}
            {!result && !loading && (
                <div
                    style={{
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        justifyContent: "center",
                        minHeight: "300px",
                        color: "var(--muted)",
                        textAlign: "center",
                        gap: "12px",
                    }}
                >
                    <div style={{ fontSize: "2.5rem" }}>🔍</div>
                    <div style={{ fontSize: "0.875rem", maxWidth: "240px", lineHeight: 1.6 }}>
                        Wypełnij formularz i kliknij <strong style={{ color: "var(--text)" }}>Wyceń auto</strong>
                    </div>
                </div>
            )}
        </div>
    );
}