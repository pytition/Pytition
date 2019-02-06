#!/bin/bash

cd pytition
echo "Creating 3 Organizations (RAP, Greenpeace and Attac)..."
python3 ./cli_pytition.py gen_orga --orga RAP
python3 ./cli_pytition.py gen_orga --orga Greenpeace
python3 ./cli_pytition.py gen_orga --orga Attac

echo "Creating 3 users (john, max, julia)..."
python3 ./cli_pytition.py gen_user --username john --first-name John --last-name Smith -p john
python3 ./cli_pytition.py gen_user --username max --first-name Max --last-name More -p max
python3 ./cli_pytition.py gen_user --username julia --first-name Julia --last-name Steven -p julia

echo "Make John join RAP and Greenpeace..."
python3 ./cli_pytition.py join_org --orga RAP --user john
python3 ./cli_pytition.py join_org --orga Greenpeace --user john

echo "Make Julia join Greenpeace and Attac"
python3 ./cli_pytition.py join_org --orga Attac --user julia
python3 ./cli_pytition.py join_org --orga Greenpeace --user julia

echo "Make Max join Attac and RAP..."
python3 ./cli_pytition.py join_org --orga Attac --user max
python3 ./cli_pytition.py join_org --orga RAP --user max

echo "Creating petitions for each user and each organization..."
python3 ./cli_pytition.py generate_petitions -n 10 --orga RAP
python3 ./cli_pytition.py generate_petitions -n 10 --orga Greenpeace
python3 ./cli_pytition.py generate_petitions -n 10 --orga Attac
python3 ./cli_pytition.py generate_petitions -n 10 --user john
python3 ./cli_pytition.py generate_petitions -n 10 --user max
python3 ./cli_pytition.py generate_petitions -n 10 --user julia
