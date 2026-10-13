// Shared look for the notebook / binder theme.

import type { CSSProperties } from "react";

export const fontDisplay = { fontFamily: "var(--font-display), Georgia, serif" };
export const fontHand = { fontFamily: "var(--font-hand), cursive" };

// Faint blue ruled lines with a red margin line, like notebook paper.
export const ruledPaper: CSSProperties = {
    backgroundColor: "#fffdf7",
    backgroundImage: [
        "linear-gradient(to right, transparent 54px, #e8a3a3 54px, #e8a3a3 56px, transparent 56px)",
        "repeating-linear-gradient(to bottom, transparent 0, transparent 31px, #dce6f2 31px, #dce6f2 32px)",
    ].join(","),
};

// Colored tabs for documents in the binder. Colors follow each document's
// position in the binder, so neighbouring tabs never share a color.
const TAB_COLORS = [
    { bg: "#fde68a", text: "#78350f" },  // yellow
    { bg: "#bfdbfe", text: "#1e3a8a" },  // blue
    { bg: "#bbf7d0", text: "#14532d" },  // green
    { bg: "#fecaca", text: "#7f1d1d" },  // red
    { bg: "#ddd6fe", text: "#4c1d95" },  // purple
    { bg: "#fed7aa", text: "#7c2d12" },  // orange
];

export function tabColor(name: string, documents: string[]) {

    let index = documents.indexOf(name);

    // A source whose document was since removed: fall back to a stable pick
    if (index === -1) {
        index = 0;
        for (const char of name) {
            index = (index * 31 + char.charCodeAt(0)) >>> 0;
        }
    }

    return TAB_COLORS[index % TAB_COLORS.length];
}

export function displayName(fileName: string) {
    return fileName.replace(/\.(pdf|txt|md)$/i, "");
}
