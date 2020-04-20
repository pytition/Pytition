#!/bin/bash

echo "Running database migrations"

cd pytition && python3 ./manage.py migrate && cd -

echo "Installing static files"

cd pytition && python3 ./manage.py collectstatic && cd -

echo "Generating translation files"

cd pytition && python3 ./manage.py compilemessages && cd -

echo "Creating superuser account"

cd pytition && python3 ./manage.py createsuperuser && cd -

echo "Done"

echo "Do you want to pre-populate the database with some users, organizations and petitions? (y/N)"

read prepopulate

if [ "${prepopulate}" == "y" ] || [ "${prepopulate}" == "yes" ]
then
    ./dev/prepopulate.sh
fi
