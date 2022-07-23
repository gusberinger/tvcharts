FROM python:3

WORKDIR /app
COPY requirements.txt .
COPY src/dump/db.sqlite src/dump/db.sqlite
COPY src/server.py src/server.py
RUN pip install -r requirements.txt
CMD ["python", "src/server.py"]