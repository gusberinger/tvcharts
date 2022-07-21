FROM python:3

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
RUN ["python", "src/build_database.py"]
CMD ["python", "src/server.py"]