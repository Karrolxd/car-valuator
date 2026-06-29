"use client";

import type { PredictResponse, Confidence } from "@/lib/types";
import { PriceDistributionChart } from "@/components/PriceDistributionChart";
import { SimilarListingsTable } from "@/components/SimilarListingsTable";

const CONFIDENCE_CONFIG: Record<
    Confidence,
    { label: string; color: string; bg: string; desc: string }
> = {
    high: {
        label: "Wysoka",
        color: "#22c55e",
        bg: "rgba(34,197,94,0.1)",
        desc: "Wycena oparta na 30+ podobnych ogłoszeniach",
    },
    medium: {
        label: "Średnia",
        color: "#f59e0b",
        bg: "rgba(245,158,11,0.1)",
        desc: "Wycena oparta na 10-29 podobnych ogłoszeniach",
    },
    low: {
        label: "Niska",
        color: "#ef4444",
        bg: "rgba(239,68,68,0.1)",
        desc: "Mało danych — wynik może być mniej dokładny",
    },
};

function formatPrice(price: number): string {
    return price.toLocaleString("pl-PL");
}

interface Props {
    result: PredictResponse;
}

export function PriceResult({ result }: Props) {
    const conf = CONFIDENCE_CONFIG[result.confidence];

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            {/* Główna cena */}
            <div
                className="card"
                style={{
                    background:
                        "linear-gradient(135deg, #1a1a28 0%, #1e1e35 100%)",
                    border: "1px solid var(--border)",
                    position: "relative",
                    overflow: "hidden",
                }}
            >
                {/* Accent glow */}
                <div
                    style={{
                        position: "absolute",
                        top: "-40px",
                        right: "-40px",
                        width: "160px",
                        height: "160px",
                        background: "rgba(61,111,255,0.08)",
                        borderRadius: "50%",
                        pointerEvents: "none",
                    }}
                />

                <p className="label" style={{ marginBottom: "12px" }}>
                    Szacowana wartość rynkowa
                </p>

                <div
                    className="num"
                    style={{
                        fontSize: "clamp(2rem, 5vw, 3rem)",
                        fontWeight: 900,
                        letterSpacing: "-0.04em",
                        color: "var(--accent)",
                        lineHeight: 1,
                        marginBottom: "16px",
                    }}
                >
                    {formatPrice(result.predicted_price_pln)}{" "}
                    <span style={{ fontSize: "0.45em", fontWeight: 600, color: "var(--muted)" }}>
            PLN
          </span>
                </div>

                {/* Przedział min-max */}
                <div
                    style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        padding: "12px 16px",
                        background: "rgba(255,255,255,0.03)",
                        borderRadius: "8px",
                        marginBottom: "16px",
                    }}
                >
                    <div style={{ flex: 1, textAlign: "center" }}>
                        <div className="label" style={{ marginBottom: "4px" }}>Min (P10)</div>
                        <div
                            className="num"
                            style={{ fontWeight: 700, fontSize: "1.1rem" }}
                        >
                            {formatPrice(result.price_range.min)}{" "}
                            <span style={{ fontSize: "0.75em", color: "var(--muted)" }}>zł</span>
                        </div>
                    </div>
                    <div
                        style={{
                            width: "1px",
                            height: "32px",
                            background: "var(--border)",
                        }}
                    />
                    <div style={{ flex: 1, textAlign: "center" }}>
                        <div className="label" style={{ marginBottom: "4px" }}>Max (P90)</div>
                        <div
                            className="num"
                            style={{ fontWeight: 700, fontSize: "1.1rem" }}
                        >
                            {formatPrice(result.price_range.max)}{" "}
                            <span style={{ fontSize: "0.75em", color: "var(--muted)" }}>zł</span>
                        </div>
                    </div>
                </div>

                {/* Confidence badge */}
                <div
                    style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "8px",
                        padding: "6px 12px",
                        background: conf.bg,
                        border: `1px solid ${conf.color}33`,
                        borderRadius: "6px",
                    }}
                >
                    <div
                        style={{
                            width: "6px",
                            height: "6px",
                            borderRadius: "50%",
                            background: conf.color,
                            flexShrink: 0,
                        }}
                    />
                    <span
                        style={{
                            fontSize: "0.75rem",
                            fontWeight: 600,
                            color: conf.color,
                        }}
                    >
            Pewność: {conf.label}
          </span>
                    <span
                        style={{
                            fontSize: "0.75rem",
                            color: "var(--muted)",
                        }}
                    >
            · {conf.desc}
          </span>
                </div>
            </div>

            {/* Statystyki */}
            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "12px",
                }}
            >
                <div className="card" style={{ padding: "16px", textAlign: "center" }}>
                    <div className="label" style={{ marginBottom: "6px" }}>
                        Podobnych ogłoszeń
                    </div>
                    <div
                        className="num"
                        style={{ fontSize: "1.75rem", fontWeight: 800 }}
                    >
                        {result.comparables_count}
                    </div>
                </div>
                <div className="card" style={{ padding: "16px", textAlign: "center" }}>
                    <div className="label" style={{ marginBottom: "6px" }}>
                        Rozstęp cen
                    </div>
                    <div
                        className="num"
                        style={{ fontSize: "1.75rem", fontWeight: 800 }}
                    >
                        {formatPrice(result.price_range.max - result.price_range.min)}{" "}
                        <span style={{ fontSize: "0.5em", color: "var(--muted)" }}>zł</span>
                    </div>
                </div>
                {result.price_distribution.length > 0 && (
                    <PriceDistributionChart
                        data={result.price_distribution}
                        predictedPrice={result.predicted_price_pln}
                    />
                )}
                {result.similar_listings.length > 0 && (
                    <SimilarListingsTable listings={result.similar_listings} />
                )}
            </div>
        </div>
    );
}