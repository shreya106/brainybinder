"use client";

import { useEffect, useState } from "react";

import UploadSection from "../components/UploadSection";
import DocumentList from "../components/DocumentList";
import QuestionSection from "../components/QuestionSection";
import AnswerSection from "../components/AnswerSection";

import {
    getDocuments,
    askQuestion
} from "../lib/api";

type Source = {
    source: string;
    chunk: number;
    preview: string;
};

export default function Home() {

    const [documents, setDocuments] = useState<string[]>([]);
    const [answer, setAnswer] = useState("");
    const [sources, setSources] = useState<Source[]>([]);

    async function loadDocuments() {

        try {

            const result = await getDocuments();

            setDocuments(result.documents);

        } catch (error) {

            console.error(error);

        }

    }

    async function handleQuestion(question: string) {

        try {

            const result = await askQuestion(question);

            setAnswer(result.answer);

            setSources(result.sources);

        } catch (error) {

            console.error(error);

        }

    }

    useEffect(() => {

        loadDocuments();

    }, []);

    return (

        <main className="min-h-screen bg-slate-100">

            <div className="max-w-7xl mx-auto px-8 py-10">

                <div className="mb-10">

                    <h1 className="text-5xl font-bold text-center text-slate-900">

                        BrainyBinder

                    </h1>

                    <p className="text-center text-slate-500 mt-3 text-lg">

                        Your AI powered personal knowledge assistant

                    </p>

                </div>

                <div className="grid grid-cols-12 gap-8">

                    {/* LEFT PANEL */}

                    <div className="col-span-4 space-y-6">

                        <UploadSection
                            onUploadSuccess={loadDocuments}
                        />

                        <DocumentList
                            documents={documents}
                        />

                    </div>

                    {/* RIGHT PANEL */}

                    <div className="col-span-8 space-y-6">

                        <QuestionSection
                            onAsk={handleQuestion}
                        />

                        <AnswerSection
                            answer={answer}
                            sources={sources}
                        />

                    </div>

                </div>

            </div>

        </main>

    );

}