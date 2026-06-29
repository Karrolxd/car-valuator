"use client";

import type { SimilarListing } from "@/lib/types";

const FUEL_LABELS: Record<string, string> = {
    petrol: "Benzyna",
    diesel: "Diesel",
    hybrid: "Hybryda",
    phev: "Plug-in",
    electric: "Elektryczny",
    lpg: "LPG",
};

const GEARBOX_LABELS: Record<string, string> = {
    manual: "Manualna",
    automatic: "Automatyczna",
};

interface Props {
    listings: SimilarListing[];
}

export function SimilarListingsTable({ listings }: Props) {
    if (!listings.length) return null;

    return (
        <div className="card">
            <p className="label" style={{ marginBottom: "4px" }}>
                Podobne ogłoszenia
            </p>
            <p style={{ fontSize: "0.8rem", color: "var(--muted)", marginBottom: "16px" }}>
                5 ogłoszeń najbliższych wycenie — kliknij aby zobaczyć na Otomoto
            </p>

            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {listings.map((listing, index) => (
                    <a
                        key={listing.id}
                        href={listing.url ?? "#"}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "12px",
                            padding: "12px 14px",
                            background: "rgba(255,255,255,0.02)",
                            border: "1px solid var(--border)",
                            borderRadius: "8px",
                            textDecoration: "none",
                            color: "var(--text)",
                            transition: "border-color 0.15s ease, background 0.15s ease",
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.borderColor = "var(--accent)";
                            e.currentTarget.style.background = "rgba(61,111,255,0.05)";
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.borderColor = "var(--border)";
                            e.currentTarget.style.background = "rgba(255,255,255,0.02)";
                        }}
                    >
                        {/* Numer */}
                        <div
                            style={{
                                width: "24px",
                                height: "24px",
                                borderRadius: "6px",
                                background: "var(--border)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                fontSize: "0.7rem",
                                fontWeight: 700,
                                color: "var(--muted)",
                                flexShrink: 0,
                            }}
                        >
                            {index + 1}
                        </div>

                        {/* Info */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                            <div
                                style={{
                                    display: "flex",
                                    gap: "8px",
                                    flexWrap: "wrap",
                                    marginBottom: "4px",
                                }}
                            >
                                {listing.year && (
                                    <span style={{ fontSize: "0.8rem", fontWeight: 600 }}>
                    {listing.year}
                  </span>
                                )}
                                {listing.mileage_km && (
                                    <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                    {listing.mileage_km.toLocaleString("pl-PL")} km
                  </span>
                                )}
                                {listing.fuel_type && (
                                    <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                    {FUEL_LABELS[listing.fuel_type] ?? listing.fuel_type}
                  </span>
                                )}
                                {listing.gearbox && (
                                    <span style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                    {GEARBOX_LABELS[listing.gearbox] ?? listing.gearbox}
                  </span>
                                )}
                            </div>
                            {listing.city && (
                                <div style={{ fontSize: "0.75rem", color: "var(--muted)" }}>
                                    📍 {listing.city}
                                </div>
                            )}
                        </div>

                        {/* Cena */}
                        <div style={{ textAlign: "right", flexShrink: 0 }}>
                            <div
                                className="num"
                                style={{ fontWeight: 700, fontSize: "0.95rem" }}
                            >
                                {listing.price_pln?.toLocaleString("pl-PL")} zł
                            </div>
                            <div style={{ fontSize: "0.7rem", color: "var(--accent)" }}>
                                Otomoto →
                            </div>
                        </div>
                    </a>
                ))}
            </div>
        </div>
    );
}