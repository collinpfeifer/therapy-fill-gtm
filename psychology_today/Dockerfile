FROM python:3.10-slim
WORKDIR /app
COPY email_tracking.py /app
RUN pip install --no-cache-dir --upgrade fastapi[standard]
CMD ["fastapi", "run", "email_tracking.py", "--port", "8000"]
