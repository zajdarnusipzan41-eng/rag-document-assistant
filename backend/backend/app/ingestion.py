import io
from pypdf import PdfReader

def process_file_content(filename: str, content: bytes, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    text = ""
    
    # 1. Извлечение текста в зависимости от формата
    if filename.endswith(".pdf"):
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    elif filename.endswith(".txt") or filename.endswith(".md"):
        text = content.decode("utf-8")
    else:
        raise ValueError("Неподдерживаемый формат. Используйте PDF, TXT или MD.")

    if not text.strip():
        raise ValueError("Файл пуст или текст не удалось прочитать.")

    # 2. Нарезка на перекрывающиеся чанки
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
