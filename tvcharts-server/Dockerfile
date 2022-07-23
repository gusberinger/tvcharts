FROM python:3

WORKDIR /app
COPY requirements.txt .
COPY src/dump/db.sqlite src/dump/db.sqlite
COPY src/server.py src/server.py
# COPY src/server.py src/build_database.py

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
# RUN ["python", "src/build_database.py"]
CMD ["python", "src/server.py"]