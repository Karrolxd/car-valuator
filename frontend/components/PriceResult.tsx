"use client";

import type { PredictResponse } from "@/lib/types";

export function PriceResult({ result }: { result: PredictResponse }) {
    return (
        <div className="card">
            <p className="label" style={{ marginBottom: "8px" }}>Wycena</p>
            <div className="num" style={{ fontSize: "2.5rem", fontWeight: 800, color: "var(--accent)" }}>
                {result.predicted_price_pln.toLocaleString("pl-PL")} zł
            </div>
        </div>
    );
}