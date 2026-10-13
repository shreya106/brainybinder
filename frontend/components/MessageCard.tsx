"use client";

import { useState } from "react";

import type { Source } from "../lib/api";
import { displayName, fontDisplay, fontHand, tabColor } from "./theme";

export type Message =
    | { id: string; role: "user"; text: string }
    | {
          id: string;
          role: "assistant";
          text: string;
          mode: "question" | "summary";
          sources: Source[];
      }
    | { id: string; role: "error"; text: string; retryQuestion: string };

const BEYOND_MARKER = "Beyond your notes:";

// The backend writes plain text with short headings on their own line.
// A short line with no ending punctuation, followed by more text, is a heading.
function AnswerText({ text }: { text: string }) {

    const blocks = text.split(/\n{2,}/).map((block) => block.trim()).filter(Boolean);

    return (
        <div className="space-y-3">
            {blocks.map((block, index) => {

                const [firstLine, ...rest] = block.split("\n");
                const isHeading =
                    firstLine.length <= 70 && !/[.!?:,;]$/.test(firstLine.trim());

                if (isHeading && rest.length > 0) {
                    return (
                        <div key={index}>
                            <h3 className="mb-1 text-lg font-semibold text-[#2f4a3a]" style={fontDisplay}>
                                {firstLine}
                            </h3>
                            <p className="whitespace-pre-wrap">{rest.join("\n")}</p>
                        </div>
                    );
                }

                if (isHeading && blocks[index + 1] && block.length <= 70) {
                    return (
                        <h3 key={index} className="pt-1 text-lg font-semibold text-[#2f4a3a]" style={fontDisplay}>
                            {block}
                        </h3>
                    );
                }

                return (
                    <p key={index} className="whitespace-pre-wrap">
                        {block}
                    </p>
                );
            })}
        </div>
    );
}

function Sources({
    sources,
    mode,
    documents,
}: {
    sources: Source[];
    mode: "question" | "summary";
    documents: string[];
}) {

    const [open, setOpen] = useState<number | null>(null);

    if (sources.length === 0) return null;

    return (
        <div className="mt-5 border-t border-dashed border-[#c9bfa6] pt-3">

            <p className="text-lg text-[#6b6150]" style={fontHand}>
                {mode === "summary" ? "summarized from" : "found in"}
            </p>

            <div className="mt-1 flex flex-wrap gap-2">
                {sources.map((source, index) => {

                    const color = tabColor(source.source, documents);
                    const label = source.chunk === "all"
                        ? `${displayName(source.source)} · whole document`
                        : source.page
                            ? `${displayName(source.source)} · p. ${source.page}`
                            : displayName(source.source);

                    return (
                        <button
                            key={index}
                            onClick={() => setOpen(open === index ? null : index)}
                            aria-expanded={open === index}
                            className="rounded-md px-2.5 py-1 text-xs font-semibold shadow-sm transition hover:brightness-95"
                            style={{ backgroundColor: color.bg, color: color.text }}
                        >
                            {label}
                        </button>
                    );
                })}
            </div>

            {open !== null && sources[open] && (
                <blockquote className="mt-3 rounded-md border-l-4 border-[#c9bfa6] bg-[#f6f1e6] px-4 py-3 text-sm leading-6 text-[#4a4335]">
                    {sources[open].preview}
                    {sources[open].chunk !== "all" && "…"}
                </blockquote>
            )}

        </div>
    );
}

type Props = {
    message: Message;
    documents: string[];
    onRetry: (question: string) => void;
};

export default function MessageCard({ message, documents, onRetry }: Props) {

    const [copied, setCopied] = useState(false);

    if (message.role === "user") {
        return (
            <div className="flex justify-end">
                <div className="max-w-[80%] -rotate-[0.6deg] rounded-sm bg-[#fde68a] px-5 py-3 text-[#3d2f0a] shadow-[2px_3px_0_rgba(0,0,0,0.08)]">
                    <p className="text-base text-[#78350f]/70" style={fontHand}>you asked</p>
                    <p className="whitespace-pre-wrap text-[15px] leading-6">{message.text}</p>
                </div>
            </div>
        );
    }

    if (message.role === "error") {
        return (
            <div role="alert" className="rounded-lg border border-[#f3b4b4] bg-[#fff1f1] px-5 py-4 text-[#7f1d1d]">
                <p className="text-sm">{message.text}</p>
                <button
                    onClick={() => onRetry(message.retryQuestion)}
                    className="mt-2 text-sm font-semibold underline underline-offset-2 hover:no-underline"
                >
                    Try again
                </button>
            </div>
        );
    }

    const [fromNotes, beyond] = message.text.includes(BEYOND_MARKER)
        ? message.text.split(BEYOND_MARKER, 2).map((part) => part.trim())
        : [message.text.trim(), ""];

    async function copy() {
        try {
            await navigator.clipboard.writeText(message.text);
            setCopied(true);
            setTimeout(() => setCopied(false), 1500);
        } catch {
            // Clipboard can be blocked; nothing else to do
        }
    }

    return (
        <article className="relative rounded-lg border border-[#e4dcc8] bg-white/80 px-6 py-5 text-[16px] leading-7 text-[#2b2a26] shadow-[0_1px_0_rgba(0,0,0,0.04)]">

            <div className="mb-2 flex items-center justify-between">
                <p className="text-lg text-[#2f4a3a]" style={fontHand}>
                    {message.mode === "summary" ? "summary" : "binder says"}
                </p>
                <button
                    onClick={copy}
                    className="rounded px-2 py-1 text-xs font-semibold text-[#6b6150] hover:bg-[#f6f1e6]"
                >
                    {copied ? "Copied" : "Copy"}
                </button>
            </div>

            {fromNotes && <AnswerText text={fromNotes} />}

            {beyond && (
                <div className="mt-4 rounded-md border border-dashed border-[#9db4cf] bg-[#f2f6fb] px-4 py-3">
                    <p className="text-lg text-[#1e3a8a]" style={fontHand}>
                        beyond your notes
                    </p>
                    <div className="text-[15px] text-[#2b3a52]">
                        <AnswerText text={beyond} />
                    </div>
                </div>
            )}

            <Sources sources={message.sources} mode={message.mode} documents={documents} />

        </article>
    );
}
