#!/bin/bash

echo "Running database migrations"

cd pytition && python3 ./manage.py migrate && cd -

echo "Creating superuser account"

cd pytition && python3 ./manage.py createsuperuser && cd -

echo "Done"

echo "Do you want to pre-populate the database with some users, organizations and petitions?"

read prepopulate

if [ "${prepopulate}" == "y" ]
then
    ./dev/prepopulate.sh
fi
