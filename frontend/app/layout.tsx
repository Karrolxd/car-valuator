import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
    subsets: ["latin"],
    variable: "--font-inter",
    display: "swap",
});

export const metadata: Metadata = {
    title: "Wyceniarka samochodów | Sprawdź cenę rynkową",
    description:
        "Sprawdź rynkową cenę używanego samochodu na podstawie dziesiątek tysięcy ogłoszeń z Otomoto.",
};

export default function RootLayout({
                                       children,
                                   }: {
    children: React.ReactNode;
}) {
    return (
        <html lang="pl" className={inter.variable}>
        <body style={{ background: "var(--bg)", color: "var(--text)" }}>
        <header
            style={{
                borderBottom: "1px solid var(--border)",
                padding: "16px 24px",
            }}
        >
            <div style={{ maxWidth: "1100px", margin: "0 auto", display: "flex", alignItems: "center", gap: "12px" }}>
                <div
                    style={{
                        width: "32px",
                        height: "32px",
                        background: "var(--accent)",
                        borderRadius: "8px",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: "16px",
                    }}
                >
                    🚗
                </div>
                <div>
                    <div style={{ fontWeight: 700, fontSize: "0.95rem", letterSpacing: "-0.01em" }}>
                        Wyceniarka
                    </div>
                    <div style={{ fontSize: "0.7rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
                        Rynkowa cena auta
                    </div>
                </div>
            </div>
        </header>
        <main
            style={{
                maxWidth: "1100px",
                margin: "0 auto",
                padding: "40px 24px",
            }}
        >
            {children}
        </main>
        <footer
            style={{
                borderTop: "1px solid var(--border)",
                padding: "20px 24px",
                textAlign: "center",
                color: "var(--muted)",
                fontSize: "0.75rem",
                marginTop: "40px",
            }}
        >
            Dane z Otomoto · Model ML trenowany na {">"}50 000 ogłoszeń
        </footer>
        </body>
        </html>
    );
}