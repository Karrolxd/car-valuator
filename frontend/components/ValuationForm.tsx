"use client";

import type { Brand } from "@/lib/types";

export function ValuationForm({ brands }: { brands: Brand[] }) {
    return (
        <div className="text-gray-400">
            Formularz wyceny — w budowie ({brands.length} marek)
        </div>
    );
}