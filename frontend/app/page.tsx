"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import Binder from "../components/Binder";
import Composer from "../components/Composer";
import MessageCard, { type Message } from "../components/MessageCard";
import { displayName, fontDisplay, fontHand, ruledPaper } from "../components/theme";
import { askQuestion, getDocuments, type HistoryTurn } from "../lib/api";

const HISTORY_TURNS = 3;

function newId() {
    return Math.random().toString(36).slice(2);
}

// Pair up the latest questions with their answers for follow-ups
function buildHistory(messages: Message[]): HistoryTurn[] {

    const turns: HistoryTurn[] = [];

    for (let i = 0; i < messages.length - 1; i++) {
        const current = messages[i];
        const next = messages[i + 1];
        if (current.role === "user" && next.role === "assistant") {
            turns.push({ question: current.text, answer: next.text });
        }
    }

    return turns.slice(-HISTORY_TURNS);
}

export default function Home() {

    const [documents, setDocuments] = useState<string[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [busy, setBusy] = useState(false);
    const [loadError, setLoadError] = useState("");
    const [showBinder, setShowBinder] = useState(false);

    const bottomRef = useRef<HTMLDivElement>(null);

    const loadDocuments = useCallback(async () => {
        try {
            const result = await getDocuments();
            setDocuments(result.documents);
            setLoadError("");
        } catch (err) {
            setLoadError(err instanceof Error ? err.message : "Could not load your documents.");
        }
    }, []);

    useEffect(() => {
        loadDocuments();
    }, [loadDocuments]);

    // Keep the newest message in view
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, [messages, busy]);

    async function ask(question: string) {

        if (busy) return;

        setShowBinder(false);

        // When retrying, drop the failed attempt (the question and its error)
        const base: Message[] = [];

        messages.forEach((m, i) => {
            const next = messages[i + 1];
            const isFailedError = m.role === "error" && m.retryQuestion === question;
            const isFailedQuestion =
                m.role === "user" && m.text === question &&
                next?.role === "error" && next.retryQuestion === question;
            if (!isFailedError && !isFailedQuestion) base.push(m);
        });

        const history = buildHistory(base);

        setMessages([...base, { id: newId(), role: "user", text: question }]);
        setBusy(true);

        try {

            const result = await askQuestion(question, history);

            setMessages((current) => [
                ...current,
                {
                    id: newId(),
                    role: "assistant",
                    text: result.answer,
                    mode: result.mode,
                    sources: result.sources,
                },
            ]);

        } catch (err) {

            setMessages((current) => [
                ...current,
                {
                    id: newId(),
                    role: "error",
                    text: err instanceof Error ? err.message : "Something went wrong.",
                    retryQuestion: question,
                },
            ]);

        } finally {

            setBusy(false);

        }
    }

    // Suggested first questions: summaries always work, because they read
    // the whole document instead of searching for a matching passage.
    const starters = documents.slice(0, 3).map((doc) => ({
        label: `Summarize ${displayName(doc)}`,
        question: `Summarize ${doc}`,
    }));

    return (

        <div className="flex h-dvh bg-[#e9e2d0]">

            {/* Binder: always visible on large screens, a drawer on small ones */}
            <div
                className={`fixed inset-y-0 left-0 z-30 w-[300px] transform transition-transform lg:static lg:translate-x-0
                    ${showBinder ? "translate-x-0" : "-translate-x-full"}`}
            >
                <Binder
                    documents={documents}
                    onDocumentsChanged={loadDocuments}
                    onNewChat={() => { setMessages([]); setShowBinder(false); }}
                    onAsk={ask}
                    busy={busy}
                />
            </div>

            {showBinder && (
                <button
                    aria-label="Close binder"
                    onClick={() => setShowBinder(false)}
                    className="fixed inset-0 z-20 bg-black/30 lg:hidden"
                />
            )}

            {/* Notebook page */}
            <main className="flex min-w-0 flex-1 flex-col p-3 sm:p-5 lg:pl-8">

                <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-lg shadow-[0_8px_24px_rgba(60,45,20,0.12)]" style={ruledPaper}>

                    {/* Top bar on small screens */}
                    <div className="flex items-center gap-3 border-b border-[#e4dcc8] px-4 py-3 lg:hidden">
                        <button
                            onClick={() => setShowBinder(true)}
                            className="rounded-md bg-[#2f4a3a] px-3 py-1.5 text-sm font-semibold text-[#f3ecd8]"
                        >
                            Binder
                        </button>
                        <span className="text-lg font-semibold text-[#2f4a3a]" style={fontDisplay}>
                            BrainyBinder
                        </span>
                    </div>

                    <div className="min-h-0 flex-1 overflow-y-auto">

                        <div className="mx-auto max-w-3xl space-y-6 py-8 pl-[72px] pr-5 sm:pr-8">

                            {loadError && (
                                <div role="alert" className="rounded-lg border border-[#f3b4b4] bg-[#fff1f1] px-5 py-4 text-sm text-[#7f1d1d]">
                                    {loadError}
                                </div>
                            )}

                            {messages.length === 0 && (
                                <div className="pt-6">

                                    <h2 className="text-4xl font-semibold leading-tight text-[#2b2a26]" style={fontDisplay}>
                                        What do you want to revise today?
                                    </h2>

                                    <p className="mt-3 text-2xl text-[#6b6150]" style={fontHand}>
                                        {documents.length > 0
                                            ? `${documents.length} document${documents.length === 1 ? "" : "s"} in your binder — ask anything`
                                            : "add a PDF to your binder to begin"}
                                    </p>

                                    {starters.length > 0 && (
                                        <div className="mt-8 flex flex-col items-start gap-2">
                                            {starters.map((starter) => (
                                                <button
                                                    key={starter.question}
                                                    onClick={() => ask(starter.question)}
                                                    className="rounded-md border border-[#d8ceb6] bg-white/70 px-4 py-2 text-left text-sm text-[#3d382c]
                                                               transition hover:border-[#2f4a3a] hover:bg-white"
                                                >
                                                    {starter.label}
                                                </button>
                                            ))}
                                        </div>
                                    )}

                                </div>
                            )}

                            {messages.map((message) => (
                                <MessageCard
                                    key={message.id}
                                    message={message}
                                    documents={documents}
                                    onRetry={ask}
                                />
                            ))}

                            {busy && (
                                <p role="status" className="animate-pulse text-2xl text-[#6b6150]" style={fontHand}>
                                    flipping through your notes…
                                </p>
                            )}

                            <div ref={bottomRef} />

                        </div>

                    </div>

                    <div className="border-t border-[#e4dcc8] bg-[#fffdf7]/95 px-4 py-4 sm:px-8">
                        <div className="mx-auto max-w-3xl">
                            <Composer onSend={ask} busy={busy} />
                            <p className="mt-2 text-center text-xs text-[#9a917e]">
                                Answers come from your notes. Anything extra is marked “beyond your notes”.
                            </p>
                        </div>
                    </div>

                </div>

            </main>

        </div>

    );
}
