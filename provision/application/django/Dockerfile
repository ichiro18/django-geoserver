FROM ilyamachetto/django-base

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt
COPY . /app/

# CHECK DATABASE
COPY ./provision/application/django/check-database-entrypoint.sh /check-database-entrypoint
RUN sed -i 's/\r//' /check-database-entrypoint
RUN chmod +x /check-database-entrypoint

ENTRYPOINT ["/check-database-entrypoint"]