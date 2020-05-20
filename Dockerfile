FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV USE_POSTGRESQL 1

RUN apt-get update && \
    apt-get install --no-install-recommends -y gettext && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /code
RUN mkdir /config
RUN mkdir /static
RUN mkdir /mediaroot
WORKDIR /code
COPY requirements.txt requirements_dev.txt /code/
RUN pip install -r requirements_dev.txt
RUN pip install psycopg2-binary==2.8.4
COPY . /code/
COPY pytition/pytition/settings/config_example.py /config/docker_config.py
RUN touch /config/__init__.py
RUN /code/dev/generate_docker_config.sh
