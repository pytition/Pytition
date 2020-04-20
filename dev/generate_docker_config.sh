#!/bin/bash
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key as g; print(g())")
sed -i -e '/SECRET_KEY/d' /config/docker_config.py
sed -i -e '/DATABASES/d' /config/docker_config.py
sed -i -e '/STATIC_ROOT/d' /config/docker_config.py
echo "SECRET_KEY = \"${SECRET_KEY}\"" >> /config/docker_config.py
echo "STATIC_ROOT = \"/static/\"" >> /config/docker_config.py
echo "DEBUG = True" >> /config/docker_config.py
echo "ALLOWED_HOSTS.append('0.0.0.0')" >> /config/docker_config.py
