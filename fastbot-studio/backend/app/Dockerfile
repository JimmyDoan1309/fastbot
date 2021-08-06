FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

WORKDIR /

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]