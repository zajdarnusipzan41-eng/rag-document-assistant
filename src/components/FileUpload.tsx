import React, { useState } from 'react';
import { uploadDocument, UploadResponse } from '../api';

export const FileUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setStatusMessage(null);

    try {
      const res: UploadResponse = await uploadDocument(file);
      setStatusMessage(`✅ ${res.message} Создано чанков: ${res.chunks_created}`);
      setFile(null);
    } catch (err: any) {
      setStatusMessage(`❌ Ошибка: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px', marginBottom: '20px' }}>
      <h3>1. Загрузка документа (PDF / TXT)</h3>
      <input type="file" accept=".pdf,.txt,.md" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading} style={{ marginLeft: '10px' }}>
        {loading ? 'Загрузка и векторизация...' : 'Загрузить в базу'}
      </button>

      {statusMessage && <p style={{ marginTop: '10px' }}>{statusMessage}</p>}
    </div>
  );
};
