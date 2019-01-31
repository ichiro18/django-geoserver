FROM ubuntu:16.04

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8

RUN apt-get update && apt-get -y upgrade \
    # Настраиваем локали
    && apt-get install -y locales && locale-gen en_US.UTF-8  \
    # Для add-apt-repository
    && apt-get install -y software-properties-common curl

RUN apt-get update \
    # -------- Добавляем репозитории --------
    # requere python
    && add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update \
    # Устанавливаем python
    && apt-get install -y python3.6 python3.6-dev python3-pip\
    && ln -s /usr/bin/python3.6 /usr/local/bin/python \
    # Устанавливаем pip
    && curl https://bootstrap.pypa.io/get-pip.py | python3.6 \
    # Устанавливаем зависимости Django
    && apt-get install -y libpq-dev

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt
COPY . /app/