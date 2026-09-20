FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY dashboard ./dashboard

EXPOSE 8501

CMD ["streamlit", "run", "dashboard/main.py", "--server.address=0.0.0.0"]