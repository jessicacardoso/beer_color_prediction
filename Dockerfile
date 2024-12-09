FROM python:3.11-slim
WORKDIR /code
RUN pip install --no-cache-dir "fastapi[standard]==0.115.6" "scikit-learn==1.5.2"
COPY app /code/app
COPY models /code/models
CMD ["fastapi", "run", "app/main.py", "--port", "80", "--host", "0.0.0.0"]
