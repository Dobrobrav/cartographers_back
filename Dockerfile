FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#WORKDIR /usr/usr/web

COPY ./requirements.txt /usr/src/django/requirements.txt
RUN pip install -r /usr/src/django/requirements.txt

EXPOSE 8000