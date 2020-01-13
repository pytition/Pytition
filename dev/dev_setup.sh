#!/bin/bash

echo "Installing development dependencies"

sudo apt update
sudo apt install git virtualenv libmariadbclient-dev python3-dev build-essential

echo "Checking whether Pytition git repo is already cloned or not"

repo=$(git config remote.origin.url | sed 's/.*\/\(pytition\)/\1/I')
repo=${repo,,}

if [ "${repo}" != "pytition" ]
then
    echo "You do not appear to have cloned Pytition"
    echo "If you did, please abort this script and run it again from the cloned repository root"
    echo "If you didn't and want me to do it, hit enter. Else abort."
    read
    git clone https://github.com/pytition/pytition
    cd pytition
fi

echo "Creating virtualenv"

virtualenv -p python3 venv
source venv/bin/activate

echo "Installing Pytition Python runtime dependencies"

pip3 install -r requirements_dev.txt

echo "Install MariaDB server? (y/n)"

read mariadb

if [ "${mariadb}" == "y" ]
then
    sudo apt install mariadb-server
fi

echo "Does your SQL server install have a root password? (y/n)"

read sql_have_root_pass

if [ "${sql_have_root_pass}" == "y" ]
then
    echo "Please enter your SQL root password"
    read -p sql_root_pass
fi

echo "Creating SQL database and user"

if [ -f my.cnf ]
then
    echo "You seem to already have a my.cnf file, skip this step? (y/n)"
    read skip_sql_creation
fi

if [ "${skip_sql_creation}" != "y" ]
then

sql_pytition_pass=$(< /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c${1:-32};echo;)

sql_statement="CREATE USER pytition@localhost IDENTIFIED BY '${sql_pytition_pass}'; CREATE DATABASE pytition; GRANT USAGE ON *.* TO 'pytition'@localhost IDENTIFIED BY '${sql_pytition_pass}'; GRANT ALL privileges ON pytition.* TO pytition@localhost; FLUSH PRIVILEGES;"

if [ "${sql_have_root_pass}" == "y" ]
then
    mysql -h localhost -u root --password=${sql_root_pass} -Bse "${sql_statement}"
else
    sudo mysql -h localhost -u root -Bse "${sql_statement}"
fi

echo "Creating your sql config file my.cnf"

cat <<ENDOFFILE >> my.cnf
[client]
database = pytition
user = pytition
password = ${sql_pytition_pass}
default-character-set = utf8
ENDOFFILE

fi

echo "Updating settings to use your my.cnf"

sed -i -e "s@/home/petition/www/@$PWD/@" pytition/pytition/settings/base.py

echo "Running database migrations"

cd pytition && python3 ./manage.py migrate && cd -

echo "Creating superuser account"

cd pytition && python3 ./manage.py createsuperuser && cd -

echo "Done"

echo "Do you want to pre-populate the database with some users, organizations and petitions?"

read prepopulate

if [ "${prepopulate}" == "y" ]
then
    ./dev/prepropulate.sh
fi

echo "Done!"
echo ""
echo ""

echo "You can now run the following commands to start the development server:"
echo "$ cd pytition"
echo "$ source venv/bin/activate"
echo "$ python3 ./pytition/manage.py runserver"
