FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Referans fotograflari kopyala
COPY character_refs/ character_refs/

CMD ["python", "bot.py"]
