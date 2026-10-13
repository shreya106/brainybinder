import type { Metadata } from "next";
import { Caveat, Fraunces, Source_Sans_3 } from "next/font/google";

import "./globals.css";

// Display serif for headings, a readable sans for answers, and a
// handwritten face used sparingly for labels and tabs.
const fraunces = Fraunces({
    subsets: ["latin"],
    variable: "--font-display",
});

const sourceSans = Source_Sans_3({
    subsets: ["latin"],
    variable: "--font-body",
});

const caveat = Caveat({
    subsets: ["latin"],
    variable: "--font-hand",
});

export const metadata: Metadata = {
    title: "BrainyBinder",
    description: "Ask questions about your own notes.",
};

export default function RootLayout({
    children,
}: Readonly<{ children: React.ReactNode }>) {

    return (
        <html lang="en">
            <body
                className={`${fraunces.variable} ${sourceSans.variable} ${caveat.variable} antialiased`}
                style={{ fontFamily: "var(--font-body), system-ui, sans-serif" }}
            >
                {children}
            </body>
        </html>
    );
}
