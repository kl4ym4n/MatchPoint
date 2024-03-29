FROM python:3.11-slim

WORKDIR /MatchPoint
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="$PYTHONPATH:/MatchPoint"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../../../.. .

CMD ["python", "services/task_service/main.py"]
