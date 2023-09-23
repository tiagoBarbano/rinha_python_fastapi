FROM python:3.11.5-slim-bullseye

RUN mkdir src

COPY requirements.txt src
COPY . src

WORKDIR src
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# EXPOSE 8000
# CMD ["gunicorn", "main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "1000"]
# CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]