#!groovy
// This deployment script assumes that there is only a single Jenkins server (master) and there are no agents.
// If the setup includes agents, then the stages should be reconfigured to take advantage of additional remote nodes.
// This script is assuming that you're using a multi-branch project but the majority directly translates to a regular pipeline project.

node {
        checkout scm

        sh '''
export PATH=/var/lib/jenkins/.local/bin:$PATH # needed for pdm
cd $WORKSPACE
git fetch --tags
pdm venv remove -y in-project || echo "No pdm venv so far, continuing"
pdm sync --clean
cat <<ENDOFFILE > my.cnf
[client]
database = pytition
user = pytition
password = pytition
default-character-set = utf8
ENDOFFILE

echo "Generating a basic config file"

echo "from .base import *" > pytition/pytition/settings/config.py
echo "SECRET_KEY = '$(pdm run python3 -c "from django.core.management.utils import get_random_secret_key as g; print(g())")'" >> pytition/pytition/settings/config.py
cat <<EOT >> pytition/pytition/settings/config.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '$PWD/my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
EOT

export DJANGO_SETTINGS_MODULE=pytition.settings.config

echo "Create Pytition database from scratch"

mysql --defaults-extra-file=$PWD/my.cnf -e "drop database pytition; create database pytition;"

echo "Running database migrations"

cd pytition && pdm run python3 ./manage.py migrate && cd -

echo "Generating documentation"

cd doc && pdm run make html
cd -

echo "Compiling translations"

cd pytition && pdm run python3 ./manage.py compilemessages && cd -

echo "Running tests"

pdm run coverage erase
pdm run coverage run ./pytition/manage.py test --noinput petition
pdm run coverage xml --include='pytition/*'
           '''
step([$class: 'CoberturaPublisher',
                           autoUpdateHealth: false,
                           autoUpdateStability: false,
                           coberturaReportFile: 'coverage.xml',
                           failNoReports: false,
                           failUnhealthy: false,
                           failUnstable: false,
                           maxNumberOfBuilds: 10,
                           onlyStable: false,
                           sourceEncoding: 'ASCII',
                           zoomCoverageChart: false]
)
}
