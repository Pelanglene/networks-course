FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x /app/mtu_test.py

ENTRYPOINT ["python", "/app/mtu_test.py"]