"use client";

type Source = {
    source: string;
    chunk: number;
    preview: string;
};

type Props = {
    answer: string;
    sources: Source[];
};

export default function AnswerSection({
    answer,
    sources,
}: Props) {

    if (!answer) return null;

    async function copyAnswer() {

        await navigator.clipboard.writeText(answer);

        alert("Answer copied to clipboard!");

    }

    return (

        <div className="space-y-6">

            {/* Answer Card */}

            <div className="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">

                <div className="flex justify-between items-center bg-blue-600 px-6 py-4">

                    <h2 className="text-xl font-semibold text-white">

                        Answer

                    </h2>

                    <button

                        onClick={copyAnswer}

                        className="bg-white text-blue-600 px-4 py-2 rounded-lg text-sm font-semibold hover:bg-slate-100 transition"

                    >

                        Copy

                    </button>

                </div>

                <div className="p-6">

                    <p className="text-slate-700 leading-8 whitespace-pre-wrap">

                        {answer}

                    </p>

                </div>

            </div>

            {/* Sources */}

            <div className="bg-white rounded-2xl shadow-md border border-slate-200">

                <div className="px-6 py-4 border-b">

                    <h2 className="text-xl font-semibold text-slate-800">

                        Sources

                    </h2>

                </div>

                <div className="p-6 space-y-5">

                    {sources.map((source, index) => (

                        <div

                            key={index}

                            className="rounded-xl border border-slate-200 p-5 hover:border-blue-400 hover:shadow transition"

                        >

                            <div className="flex justify-between items-center mb-4">

                                <div>

                                    <p className="font-semibold text-slate-800">

                                        {source.source}

                                    </p>

                                    <p className="text-sm text-slate-500">

                                        Chunk {source.chunk}

                                    </p>

                                </div>

                                <div className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-medium">

                                    Retrieved

                                </div>

                            </div>

                            <div className="bg-slate-50 rounded-lg p-4">

                                <p className="text-slate-600 text-sm leading-7">

                                    {source.preview}

                                </p>

                            </div>

                        </div>

                    ))}

                </div>

            </div>

        </div>

    );

}