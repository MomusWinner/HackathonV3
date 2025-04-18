import PyPDF2
import requests
from pdf2image import convert_from_bytes
import base64
import os
import io
from PIL import Image
import threading

API_BASE_URL = "https://llm.rdfai.ru/api/providers/openai/v1"
API_KEY = "9a49054fe339d4bf09f9a35f0d7169e4f4bfacd4bc4b9594406b3348c89d8558"


def encode_image(image_bytes):
    """Кодирует байты изображения в Base64."""
    return base64.b64encode(image_bytes).decode("utf-8")


def describe_image(image_bytes, image_name):
    """Отправляет запрос к API для описания изображения."""
    try:
        image_base64 = encode_image(image_bytes)
        payload = {
            "model": "gpt-4.1",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe the content of this image in a concise manner."},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 100,
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{API_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Error describing image {image_name}: {str(e)}"


def process_image(image, page_num, output_dir, extracted_content, lock):
    """Обрабатывает одно изображение в отдельном потоке."""
    image_ext = 'png'
    image_name = f"page_{page_num + 1}_img_1.{image_ext}"
    image_path = os.path.join(output_dir, image_name)

    # Сохранение изображения во временный файл
    image.save(image_path, 'PNG')

    # Чтение байтов изображения
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()

    # Описание изображения через API
    description = describe_image(image_bytes, image_name)

    # Потокобезопасное добавление результата
    with lock:
        extracted_content.append({
            'type': 'image',
            'name': image_name,
            'description': description,
            'page': page_num + 1
        })


def extract_pdf_content(pdf_bytes, output_dir="extracted_images"):
    """Извлекает текст и описания изображений из PDF, переданного в виде байтов."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Чтение PDF из байтов
    pdf_file = io.BytesIO(pdf_bytes)
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_content = []
    lock = threading.Lock()

    # Конвертация страниц PDF в изображения из байтов
    images = convert_from_bytes(pdf_bytes, thread_count=os.cpu_count())

    # Итерация по страницам
    threads = []
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]

        # Извлечение текста
        text = page.extract_text()
        if text.strip():
            with lock:
                extracted_content.append({
                    'type': 'text',
                    'content': text,
                    'page': page_num + 1
                })

        # Обработка изображений
        if page_num < len(images):
            thread = threading.Thread(
                target=process_image,
                args=(images[page_num], page_num, output_dir, extracted_content, lock)
            )
            threads.append(thread)
            thread.start()

    # Ожидание завершения всех потоков
    for thread in threads:
        thread.join()

    # Сортировка по номеру страницы
    extracted_content.sort(key=lambda x: x['page'])

    res = ""
    for item in extracted_content:
        if item['type'] == 'text':
            res += f"\n=== Page {item['page']} Text ===\n"
            res += item['content']
            res += "\n"
        elif item['type'] == 'image':
            res += f"\n=== Page {item['page']} Image ===\n"
            res += f"Image Name: {item['name']}\n"
            res += f"Description: {item['description']}\n"
            res += "\n"

    return res

