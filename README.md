# RAG Document Assistant

Это простой RAG-проект для поиска по документам.

## Что умеет
- загрузка PDF/TXT/MD файлов
- разбиение текста на чанки
- эмбеддинги через Gemini
- поиск по векторной базе ChromaDB
- генерация ответа на вопрос по найденным чанкам

## Структура проекта
```text
project/
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── main.py
│   │   └── rag_engine.py
│   ├── .env.example
│   └── requirements.txt
├── src/
│   ├── App.tsx
│   ├── api.ts
│   ├── Chat.tsx
│   └── components/
├── README.md
└── package.json
```

## Запуск backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# затем укажи реальный GEMINI_API_KEY
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Запуск frontend
```bash
npm install
npm run dev
```

## API
- POST /api/v1/upload
- POST /api/v1/query

## Пример запроса
```json
{
  "question": "Что написано в документе?",
  "top_k": 4
}
```
