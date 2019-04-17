To use pytition with nginx/uwsgi, you need to do:

In the pytition main directory

`docker-compose -f docker-compose.yml -f nginx-uwsgi/docker-compose.yml up --build`
