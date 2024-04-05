FROM python:3.8
ENV PYTHONUNBUFFERED 1
ENV USE_POSTGRESQL 1

RUN apt-get update && \
    apt-get install --no-install-recommends -y gettext && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U pdm
RUN mkdir /code
RUN mkdir /config
RUN mkdir /static
RUN mkdir /mediaroot
RUN mkdir /venv
WORKDIR /code
COPY pyproject.toml pdm.lock /venv/
RUN cd /venv && pdm sync
RUN cd /venv && pdm add psycopg[binary]==3.1.8
RUN pdm use -f /venv/.venv
COPY . /code/
COPY pytition/pytition/settings/config_example.py /config/docker_config.py
RUN touch /config/__init__.py
RUN pdm run /code/dev/generate_docker_config.sh
