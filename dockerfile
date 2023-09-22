FROM python:3.11.5-slim-bullseye

RUN mkdir src

COPY requirements.txt src
COPY . src

WORKDIR src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8000
CMD ["gunicorn", "main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]