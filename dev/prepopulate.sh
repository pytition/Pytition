#!/bin/bash

cd pytition
echo "Creating 3 Organizations (RAP, Greenpeace and Attac)..."
python3 ./manage.py gen_orga RAP Greenpeace Attac

echo "Creating 3 users (john, max, julia)..."
python3 ./manage.py gen_user john john --first-name John --last-name Smith
python3 ./manage.py gen_user max max --first-name Max --last-name More
python3 ./manage.py gen_user julia julia --first-name Julia --last-name Steven

echo "Make John join RAP and Greenpeace..."
python3 ./manage.py join_org john RAP 
python3 ./manage.py join_org john Greenpeace 

echo "Make Julia join Greenpeace and Attac"
python3 ./manage.py join_org julia Attac 
python3 ./manage.py join_org julia Greenpeace

echo "Make Max join Attac and RAP..."
python3 ./manage.py join_org max Attac
python3 ./manage.py join_org max RAP

echo "Creating petitions for each user and each organization..."
python3 ./manage.py gen_pet -n 10 --orga RAP
python3 ./manage.py gen_pet -n 10 --orga Greenpeace
python3 ./manage.py gen_pet -n 10 --orga Attac
python3 ./manage.py gen_pet -n 10 --user john
python3 ./manage.py gen_pet -n 10 --user max
python3 ./manage.py gen_pet -n 10 --user julia
