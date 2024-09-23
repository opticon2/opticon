FROM python:3.9-slim

WORKDIR /app

RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false install -y inotify-tools

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./launch.sh /app/launch.sh

EXPOSE 80

CMD ["/app/launch.sh"]