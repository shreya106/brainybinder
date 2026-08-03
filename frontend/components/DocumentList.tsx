"use client";

type Props = {
    documents: string[];
};

export default function DocumentList({
    documents,
}: Props) {

    return (

        <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6">

            <div className="flex items-center justify-between mb-6">

                <h2 className="text-2xl font-bold text-slate-800">

                    Indexed Documents

                </h2>

                <span className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full">

                    {documents.length}

                </span>

            </div>

            {documents.length === 0 ? (

                <div className="text-center py-10">

                    <div className="text-5xl mb-3">

                        📂

                    </div>

                    <p className="text-slate-600 font-medium">

                        No documents uploaded

                    </p>

                    <p className="text-sm text-slate-400 mt-2">

                        Upload your first PDF to start asking questions.

                    </p>

                </div>

            ) : (

                <div className="space-y-4">

                    {documents.map((document) => (

                        <div
                            key={document}
                            className="border border-slate-200 rounded-xl p-4 hover:border-blue-500 hover:shadow transition"
                        >

                            <div className="flex items-center justify-between">

                                <div>

                                    <div className="flex items-center gap-3">

                                        <span className="text-3xl">

                                            📄

                                        </span>

                                        <div>

                                            <p className="font-semibold text-slate-800 break-all">

                                                {document}

                                            </p>

                                            <p className="text-sm text-slate-500">

                                                Indexed and ready for search

                                            </p>

                                        </div>

                                    </div>

                                </div>

                                <div>

                                    <span className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-semibold">

                                        Ready

                                    </span>

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </div>

    );

}