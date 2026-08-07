# 📄 RAG Document Assistant

**RAG Document Assistant** — это full-stack веб-приложение для умного поиска и ответов на вопросы по локальным документам (PDF, TXT, MD) с использованием технологий Retrieval-Augmented Generation (RAG).

Приложение принимает пользовательские файлы, разбивает их на чанки, сохраняет эмбеддинги в векторную базу данных ChromaDB и генерирует точные ответы с помощью OpenAI API, подтягивая только актуальный контекст.

---

## 🛠 Технологический стек

### **Backend**
* **Python 3.10+** & **FastAPI** — быстрый асинхронный REST API framework.
* **ChromaDB** — локальная векторная база данных для семантического поиска.
* **OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)** — векторизация текста и генерация ответов.
* **Pydantic v2** — строгая валидация данных и схем API.
* **PyPDF** — извлечение текста из PDF-документов.

### **Frontend**
* **React** & **TypeScript** — динамичный и типизированный пользовательский интерфейс.
* **Fetch API / Form Data** — асинхронное взаимодействие с FastAPI бэкендом.

---

## 🏗 Архитектура проекта

```text
RAG Document Assistant/
├── backend/
│   ├── app/
│   │   ├── main.py          # Точка входа FastAPI, CORS, подсоединение роутеров
│   │   ├── config.py        # Настройки Pydantic Settings и считывание .env
│   │   ├── schemas.py       # Pydantic-модели запросов и ответов
│   │   ├── ingestion.py     # Модуль чтения и чанкинга файлов (PDF/TXT)
│   │   ├── rag_engine.py    # Работа с ChromaDB и обращение к OpenAI API
│   │   └── routers/
│   │       ├── chat.py      # Маршрут POST /api/v1/chat/query
│   │       └── documents.py # Маршрут POST /api/v1/documents/upload
│   ├── .env.example
│   ├── .gitignore
│   └── requirements.txt
│
└── frontend/
    └── src/
        ├── api.ts           # Клиентский слой для запросов к FastAPI
        ├── App.tsx          # Главный макет приложения
        └── components/
            ├── FileUpload.tsx # Компонент загрузки и векторизации файлов
            └── Chat.tsx       # Интерфейс чата с выводом источников
