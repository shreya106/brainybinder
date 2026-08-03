"use client";

import { useState } from "react";
import { uploadDocument } from "../lib/api";

type Props = {
    onUploadSuccess: () => void;
};

export default function UploadSection({
    onUploadSuccess,
}: Props) {

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleUpload() {

        if (!selectedFile) return;

        try {

            setLoading(true);

            const result = await uploadDocument(selectedFile);

            alert(result.message);

            setSelectedFile(null);

            onUploadSuccess();

        } catch (error) {

            console.error(error);

            alert("Upload failed");

        } finally {

            setLoading(false);

        }

    }

    return (

        <div className="bg-white rounded-2xl shadow-md border border-slate-200 p-6">

            <h2 className="text-2xl font-bold text-slate-800 mb-2">

                Upload PDF

            </h2>

            <p className="text-slate-500 mb-6">

                Upload a PDF to add it to your personal knowledge base.

            </p>

            <input
                type="file"
                accept=".pdf"
                onChange={(event) => {

                    if (event.target.files) {

                        setSelectedFile(event.target.files[0]);

                    }

                }}
                className="block w-full text-sm
                           file:mr-4
                           file:py-3
                           file:px-5
                           file:rounded-lg
                           file:border-0
                           file:bg-blue-600
                           file:text-white
                           file:font-medium
                           hover:file:bg-blue-700
                           cursor-pointer"
            />

            {selectedFile && (

                <div className="mt-5 rounded-lg bg-slate-100 p-3">

                    <p className="text-sm text-slate-700">

                        <span className="font-semibold">

                            Selected File

                        </span>

                    </p>

                    <p className="text-blue-600 font-medium mt-1">

                        {selectedFile.name}

                    </p>

                </div>

            )}

            <button

                onClick={handleUpload}

                disabled={!selectedFile || loading}

                className="mt-6 w-full bg-blue-600 hover:bg-blue-700
                           text-white py-3 rounded-lg font-semibold
                           disabled:bg-slate-400
                           transition"

            >

                {loading ? "Uploading..." : "Upload Document"}

            </button>

        </div>

    );

}