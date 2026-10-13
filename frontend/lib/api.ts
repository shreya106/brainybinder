export const BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export type Source = {
    source: string;
    chunk: number | string;
    page?: number | null;
    distance?: number;
    preview: string;
};

export type AskResult = {
    answer: string;
    mode: "question" | "summary";
    sources: Source[];
};

export type HistoryTurn = {
    question: string;
    answer: string;
};

// Turns any failed request into an Error with a message people can read.
async function request<T>(path: string, options?: RequestInit): Promise<T> {

    let response: Response;

    try {
        response = await fetch(`${BASE_URL}${path}`, options);
    } catch {
        throw new Error(
            "Can't reach the BrainyBinder server. Is the backend running?"
        );
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        throw new Error(data?.detail ?? "Something went wrong. Please try again.");
    }

    return data as T;
}

export function getDocuments() {
    return request<{ documents: string[] }>("/documents");
}

export function askQuestion(question: string, history: HistoryTurn[] = []) {
    return request<AskResult>("/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, history }),
    });
}

export function uploadDocument(file: File) {

    const formData = new FormData();
    formData.append("file", file);

    return request<{ filename: string; chunks: number }>("/upload", {
        method: "POST",
        body: formData,
    });
}

export function deleteDocument(fileName: string) {
    return request<{ message: string }>(
        `/documents/${encodeURIComponent(fileName)}`,
        { method: "DELETE" }
    );
}
