#!groovy
// This deployment script assumes that there is only a single Jenkins server (master) and there are no agents.
// If the setup includes agents, then the stages should be reconfigured to take advantage of additional remote nodes.
// This script is assuming that you're using a multi-branch project but the majority directly translates to a regular pipeline project.

node {

	sh 'cd $WORKSPACE && rm -rf venv && virtualenv -p python3 venv'

        checkout scm

        sh '''
            cd $WORKSPACE
            source venv/bin/activate
            pip3 install -r requirements.txt 
            deactivate
           '''

        sh '''
cd $WORKSPACE
source venv/bin/activate
cat <<ENDOFFILE > my.cnf
[client]
database = pytition
user = pytition
password = pytition
default-character-set = utf8
ENDOFFILE

echo "Updating settings to use your my.cnf"

sed -i -e "s@/home/petition/www/@$PWD/@" pytition/pytition/settings/base.py

echo "Running database migrations"

cd pytition && python3 ./manage.py migrate && cd -

echo "Running tests"

coverage run ./pytition/manage.py test petition
deactivate
           '''
}
