"use client";

import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from "recharts";
import type { PriceBucket } from "@/lib/types";

interface Props {
    data: PriceBucket[];
    predictedPrice: number;
}

interface TooltipProps {
    active?: boolean;
    payload?: { value: number }[];
    label?: string;
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
    if (!active || !payload?.length) return null;

    return (
        <div
            style={{
                background: "var(--surface)",
                border: "1px solid var(--border)",
                borderRadius: "8px",
                padding: "10px 14px",
                fontSize: "0.8rem",
            }}
        >
            <div style={{ color: "var(--muted)", marginBottom: "4px" }}>{label}</div>
            <div style={{ fontWeight: 700 }}>
                {payload[0].value}{" "}
                <span style={{ color: "var(--muted)", fontWeight: 400 }}>ogłoszeń</span>
            </div>
        </div>
    );
}

export function PriceDistributionChart({ data, predictedPrice }: Props) {
    if (!data.length) return null;

    // Znajdź bucket z najwyższym count — podświetlimy go
    const maxCount = Math.max(...data.map((d) => d.count));

    return (
        <div className="card">
            <div style={{ marginBottom: "16px" }}>
                <p className="label" style={{ marginBottom: "4px" }}>
                    Rozkład cen podobnych aut
                </p>
                <p style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                    Ceny ogłoszeń w podobnym zakresie rocznika i przebiegu
                </p>
            </div>

            <ResponsiveContainer width="100%" height={180}>
                <BarChart
                    data={data}
                    margin={{ top: 4, right: 4, bottom: 4, left: 4 }}
                    barCategoryGap="20%"
                >
                    <XAxis
                        dataKey="bucket"
                        tick={{ fill: "var(--muted)", fontSize: 10 }}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis hide />
                    <Tooltip content={<CustomTooltip />} cursor={false} />
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                        {data.map((entry, index) => (
                            <Cell
                                key={index}
                                fill={
                                    entry.count === maxCount
                                        ? "var(--accent)"
                                        : "rgba(61,111,255,0.3)"
                                }
                            />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>

            <div
                style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    marginTop: "12px",
                    fontSize: "0.75rem",
                    color: "var(--muted)",
                }}
            >
                <div
                    style={{
                        width: "10px",
                        height: "10px",
                        borderRadius: "2px",
                        background: "var(--accent)",
                        flexShrink: 0,
                    }}
                />
                <span>Najczęstsza cena</span>
                <div
                    style={{
                        width: "10px",
                        height: "10px",
                        borderRadius: "2px",
                        background: "rgba(61,111,255,0.3)",
                        flexShrink: 0,
                        marginLeft: "8px",
                    }}
                />
                <span>Pozostałe przedziały</span>
            </div>
        </div>
    );
}