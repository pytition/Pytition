FROM tiangolo/uwsgi-nginx:python3.7

RUN apt update \
    && apt install -y netcat \
    && rm -rf /var/lib/apt/lists/*

ENV UWSGI_INI /app/uwsgi.ini
ENV PYTHONUNBUFFERED 1
ENV USE_POSTGRESQL 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt requirements_dev.txt /code/
RUN pip install -r requirements_dev.txt
RUN pip install psycopg2-binary==2.7.7

COPY ./nginx-uwsgi/nginx.conf /app/nginx.conf
COPY ./nginx-uwsgi/start_pytition.sh /start_pytition.sh
COPY ./nginx-uwsgi/uwsgi.ini /app/uwsgi.ini

ENTRYPOINT ["sh", "/start_pytition.sh"]
CMD ["/usr/bin/supervisord"]
