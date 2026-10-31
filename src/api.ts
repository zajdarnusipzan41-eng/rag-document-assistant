const API_BASE_URL = 'http://127.0.0.1:8000';

export interface SourceDocument {
  content: string;
  metadata: Record<string, any>;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
}

export interface UploadResponse {
  filename: string;
  chunks_processed: number;
  status: string;
  message?: string;
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/v1/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Ошибка при загрузке файла');
  }

  return response.json();
}

export async function sendQuery(query: string, topK: number = 3): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, top_k: topK }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Ошибка при получении ответа');
  }

  return response.json();
}
