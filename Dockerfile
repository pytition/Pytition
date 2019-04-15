FROM python:3
ENV PYTHONUNBUFFERED 1
ENV USE_POSTGRESQL 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt requirements_dev.txt /code/
RUN pip install -r requirements_dev.txt
RUN pip install psycopg2-binary==2.7.7
COPY . /code/
