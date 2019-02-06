FROM python:3
ENV PYTHONUNBUFFERED 1
ENV USE_POSTGRESQL 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip install psycopg2==2.7.7
COPY . /code/
