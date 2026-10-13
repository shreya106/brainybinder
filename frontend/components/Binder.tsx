"use client";

import { useRef, useState } from "react";

import { deleteDocument, uploadDocument } from "../lib/api";
import { displayName, fontDisplay, fontHand, tabColor } from "./theme";

type Props = {
    documents: string[];
    onDocumentsChanged: () => void | Promise<void>;
    onNewChat: () => void;
    onAsk: (question: string) => void;
    busy: boolean;
};

export default function Binder({
    documents,
    onDocumentsChanged,
    onNewChat,
    onAsk,
    busy,
}: Props) {

    const [uploading, setUploading] = useState(false);
    const [dragging, setDragging] = useState(false);
    const [notice, setNotice] = useState<{ kind: "ok" | "error"; text: string } | null>(null);

    const inputRef = useRef<HTMLInputElement>(null);

    async function upload(files: FileList | null) {

        const pdfs = Array.from(files ?? []).filter((file) =>
            file.name.toLowerCase().endsWith(".pdf")
        );

        if (pdfs.length === 0) {
            setNotice({ kind: "error", text: "Only PDF files can be added." });
            return;
        }

        setUploading(true);
        setNotice(null);

        const added: string[] = [];

        try {

            // One at a time so the server isn't flooded
            for (const file of pdfs) {
                const result = await uploadDocument(file);
                added.push(result.filename);
            }

            setNotice({
                kind: "ok",
                text: added.length === 1
                    ? `Added ${displayName(added[0])}`
                    : `Added ${added.length} documents`,
            });

        } catch (err) {

            setNotice({
                kind: "error",
                text: err instanceof Error ? err.message : "Upload failed.",
            });

        } finally {

            setUploading(false);

            if (inputRef.current) {
                inputRef.current.value = "";
            }

            await onDocumentsChanged();

        }

    }

    async function remove(fileName: string) {

        if (!window.confirm(`Remove ${displayName(fileName)} from your binder?`)) {
            return;
        }

        try {
            await deleteDocument(fileName);
            setNotice({ kind: "ok", text: `Removed ${displayName(fileName)}` });
        } catch (err) {
            setNotice({
                kind: "error",
                text: err instanceof Error ? err.message : "Could not remove it.",
            });
        } finally {
            await onDocumentsChanged();
        }

    }

    return (

        <aside className="relative flex h-full flex-col bg-[#2f4a3a] text-[#f3ecd8]">

            {/* Binder rings */}
            <div className="pointer-events-none absolute -right-3 top-0 hidden h-full flex-col justify-around py-16 lg:flex">
                {[0, 1, 2].map((ring) => (
                    <span
                        key={ring}
                        className="block h-7 w-7 rounded-full border-[5px] border-[#b8b2a3] bg-[#f6f1e6] shadow-inner"
                    />
                ))}
            </div>

            <div className="px-6 pt-7 pb-5">

                <h1 className="text-3xl font-semibold tracking-tight" style={fontDisplay}>
                    BrainyBinder
                </h1>

                <p className="mt-1 text-xl text-[#d9cfb3]" style={fontHand}>
                    your notes, answered
                </p>

                <button
                    onClick={onNewChat}
                    className="mt-5 w-full rounded-lg border border-[#f3ecd8]/30 px-4 py-2.5 text-sm font-semibold
                               transition hover:bg-[#f3ecd8]/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#fde68a]"
                >
                    + New page
                </button>

            </div>

            {/* Upload */}
            <div className="px-6">

                <label
                    onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={(e) => {
                        e.preventDefault();
                        setDragging(false);
                        upload(e.dataTransfer.files);
                    }}
                    className={`block cursor-pointer rounded-xl border-2 border-dashed px-4 py-5 text-center transition
                        ${dragging ? "border-[#fde68a] bg-[#f3ecd8]/10" : "border-[#f3ecd8]/35 hover:border-[#f3ecd8]/60"}`}
                >

                    <input
                        ref={inputRef}
                        type="file"
                        accept=".pdf,application/pdf"
                        multiple
                        className="sr-only"
                        onChange={(e) => upload(e.target.files)}
                        disabled={uploading}
                    />

                    <span className="block text-sm font-semibold">
                        {uploading ? "Adding to your binder…" : "Add PDFs"}
                    </span>

                    <span className="mt-1 block text-xs text-[#d9cfb3]">
                        {uploading ? "Reading and indexing" : "Drop files here or click to choose"}
                    </span>

                </label>

                {notice && (
                    <p
                        role={notice.kind === "error" ? "alert" : "status"}
                        className={`mt-3 rounded-lg px-3 py-2 text-xs ${
                            notice.kind === "error"
                                ? "bg-[#fecaca] text-[#7f1d1d]"
                                : "bg-[#bbf7d0] text-[#14532d]"
                        }`}
                    >
                        {notice.text}
                    </p>
                )}

            </div>

            {/* Document tabs */}
            <div className="mt-6 flex min-h-0 flex-1 flex-col">

                <p className="px-6 text-xs font-semibold uppercase tracking-[0.15em] text-[#d9cfb3]">
                    In this binder · {documents.length}
                </p>

                <ul className="mt-3 flex-1 space-y-2 overflow-y-auto px-6 pb-6">

                    {documents.length === 0 && (
                        <li className="text-sm text-[#d9cfb3]">
                            Nothing here yet. Add a PDF to get started.
                        </li>
                    )}

                    {documents.map((doc) => {

                        const color = tabColor(doc, documents);

                        return (
                            <li
                                key={doc}
                                className="group flex items-center rounded-r-lg rounded-l-sm shadow-sm"
                                style={{ backgroundColor: color.bg, color: color.text }}
                            >

                                <span className="truncate px-3 py-2 text-sm font-semibold" title={doc}>
                                    {displayName(doc)}
                                </span>

                                <div className="ml-auto flex shrink-0 items-center pr-1 opacity-70 transition group-hover:opacity-100 group-focus-within:opacity-100">

                                    <button
                                        onClick={() => onAsk(`Summarize ${doc}`)}
                                        disabled={busy}
                                        title={`Summarize ${displayName(doc)}`}
                                        className="rounded px-2 py-1 text-xs font-semibold hover:bg-black/10 disabled:opacity-40"
                                    >
                                        Summary
                                    </button>

                                    <button
                                        onClick={() => remove(doc)}
                                        title={`Remove ${displayName(doc)}`}
                                        aria-label={`Remove ${displayName(doc)}`}
                                        className="rounded px-2 py-1 text-sm hover:bg-black/10"
                                    >
                                        ×
                                    </button>

                                </div>

                            </li>
                        );
                    })}

                </ul>

            </div>

        </aside>

    );

}
