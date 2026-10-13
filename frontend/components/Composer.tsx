"use client";

import { useEffect, useRef, useState } from "react";

type Props = {
    onSend: (question: string) => void;
    busy: boolean;
};

export default function Composer({ onSend, busy }: Props) {

    const [text, setText] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Grow with the text, up to about 6 lines
    useEffect(() => {
        const element = textareaRef.current;
        if (!element) return;
        element.style.height = "auto";
        element.style.height = `${Math.min(element.scrollHeight, 168)}px`;
    }, [text]);

    function send() {
        const question = text.trim();
        if (!question || busy) return;
        onSend(question);
        setText("");
    }

    return (
        <div className="flex items-end gap-3 rounded-xl border border-[#d8ceb6] bg-white px-4 py-3 shadow-[0_2px_0_rgba(0,0,0,0.05)]
                        focus-within:border-[#2f4a3a] focus-within:ring-2 focus-within:ring-[#2f4a3a]/15">

            <label htmlFor="question" className="sr-only">Ask about your notes</label>

            <textarea
                id="question"
                ref={textareaRef}
                rows={1}
                value={text}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        send();
                    }
                }}
                placeholder="Ask about your notes, or say “summarize Java.pdf”…"
                className="max-h-[168px] flex-1 resize-none bg-transparent py-1.5 text-[15px] leading-6 text-[#2b2a26]
                           placeholder:text-[#9a917e] focus:outline-none"
            />

            <button
                onClick={send}
                disabled={!text.trim() || busy}
                className="shrink-0 rounded-lg bg-[#2f4a3a] px-5 py-2 text-sm font-semibold text-[#f3ecd8] transition
                           hover:bg-[#253b2e] disabled:cursor-not-allowed disabled:bg-[#b5ae9c]"
            >
                {busy ? "Thinking…" : "Ask"}
            </button>

        </div>
    );
}
