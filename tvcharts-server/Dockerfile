FROM python:3
RUN apt-get update
RUN apt-get install -y \
    mysql-server

# listen on 0.0.0.0
ADD bind_0.cnf /etc/mysql/conf.d/bind_0.cnf

RUN python -m pip install --upgrade pip
WORKDIR /app
ENV FLASK_APP=app.py
ENV FLASK_ENV=development
COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt
RUN sudo service mysql start
COPY . .
RUN ["python", "src/build_database.py"]
CMD ["python", "src/server.py"]