"use client";

import { useState } from "react";

type Props = {
    onAsk: (question: string) => Promise<void>;
};

export default function QuestionSection({
    onAsk,
}: Props) {

    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);

    async function handleAsk() {

        if (!question.trim()) return;

        try {

            setLoading(true);

            await onAsk(question);

        } finally {

            setLoading(false);

        }

    }

    return (

        <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6">

            <h2 className="text-2xl font-bold text-slate-800">

                Ask BrainyBinder

            </h2>

            <p className="text-slate-500 mt-2 mb-6">

                Ask questions about your uploaded documents using natural language.

            </p>

            <textarea

                rows={4}

                value={question}

                onChange={(e) => setQuestion(e.target.value)}

                onKeyDown={(e) => {

                    if (e.key === "Enter" && !e.shiftKey) {

                        e.preventDefault();

                        handleAsk();

                    }

                }}

                placeholder="Example: Explain Dependency Injection in Spring Boot..."

                className="w-full border border-slate-300 rounded-xl p-4
                           focus:outline-none
                           focus:ring-2
                           focus:ring-blue-500
                           focus:border-blue-500
                           resize-none"

            />

            <div className="mt-4 flex justify-end">

                <button

                    onClick={handleAsk}

                    disabled={!question.trim() || loading}

                    className="bg-blue-600 hover:bg-blue-700
                               text-white
                               px-8
                               py-3
                               rounded-xl
                               font-semibold
                               transition
                               disabled:bg-slate-400"

                >

                    {loading ? "Generating..." : "Ask Question"}

                </button>

            </div>

            <div className="mt-8 border-t pt-5">

                <p className="text-sm font-semibold text-slate-600 mb-3">

                    Example Questions

                </p>

                <div className="space-y-2 text-sm text-slate-500">

                    <p>
                        • What is JVM?
                    </p>

                    <p>
                        • Explain Dependency Injection.
                    </p>

                    <p>
                        • Summarize Java.pdf.
                    </p>

                    <p>
                        • Compare HashMap and TreeMap.
                    </p>

                </div>

            </div>

        </div>

    );

}