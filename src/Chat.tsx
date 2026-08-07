import React, { useState } from 'react';
import { sendQuery, SourceDocument } from '../api';

interface Message {
  sender: 'user' | 'assistant';
  text: string;
  sources?: SourceDocument[];
}

export const Chat: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendQuery(input);
      const botMessage: Message = {
        sender: 'assistant',
        text: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { sender: 'assistant', text: ` Ошибка ответа: ${err.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h3>2. Задать вопрос по документам</h3>

      <div style={{ minHeight: '300px', maxHeight: '500px', overflowY: 'auto', marginBottom: '20px' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', margin: '10px 0' }}>
            <div
              style={{
                display: 'inline-block',
                padding: '10px 14px',
                borderRadius: '12px',
                backgroundColor: msg.sender === 'user' ? '#007bff' : '#f1f1f1',
                color: msg.sender === 'user' ? '#fff' : '#333',
                maxWidth: '70%',
              }}
            >
              <p style={{ margin: 0 }}>{msg.text}</p>

              {/* Отображение источников контекста */}
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.8, textAlign: 'left' }}>
                  <strong> Источники:</strong>
                  {msg.sources.map((s, i) => (
                    <div key={i} style={{ marginTop: '4px', fontStyle: 'italic' }}>
                      • {s.metadata.filename || 'Файл'} (чанк #{s.metadata.chunk_index})
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && <p style={{ color: '#888' }}>Печатает ответ...</p>}
      </div>

      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Напишите вопрос по загруженным документам..."
          style={{ flex: 1, padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button onClick={handleSend} disabled={loading} style={{ padding: '10px 20px' }}>
          Отправить
        </button>
      </div>
    </div>
  );
};
