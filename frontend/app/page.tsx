import { getBrands } from "@/lib/api";
import { ValuationForm } from "@/components/ValuationForm";

export default async function Home() {
    const brands = await getBrands();

    return (
        <div>
            <div style={{ marginBottom: "32px" }}>
                <p className="label" style={{ marginBottom: "8px" }}>
                    Wycena pojazdu
                </p>
                <h2
                    style={{
                        fontSize: "2rem",
                        fontWeight: 800,
                        letterSpacing: "-0.03em",
                        lineHeight: 1.1,
                        marginBottom: "8px",
                    }}
                >
                    Ile warte jest Twoje auto?
                </h2>
                <p style={{ color: "var(--muted)", fontSize: "0.95rem", maxWidth: "480px" }}>
                    Podaj parametry pojazdu — porównamy je z{" "}
                    <span style={{ color: "var(--text)" }}>dziesiątkami tysięcy ogłoszeń</span>{" "}
                    i podamy rynkową wycenę.
                </p>
            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "minmax(320px, 420px) 1fr",
                    gap: "32px",
                    alignItems: "start",
                }}
            >
                <ValuationForm brands={brands} />
            </div>
        </div>
    );
}