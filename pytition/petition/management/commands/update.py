import subprocess
from functools import partial
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import os

run = partial(subprocess.run, shell=True, check=True)


class Command(BaseCommand):
    """Update pytition install
    """

    def handle(self, *args, **options):
        try:
            git_path = Path(settings.BASE_DIR).parent
            os.chdir(git_path)
            run("git checkout master && git pull")
            
            version_cmd = "curl -s https://api.github.com/repos/pytition/pytition/releases/latest | grep 'tag_name' | cut -d : -f2,3 | tr -d \\\" | tr -d ,"
            version = run(version_cmd, capture_output=True).stdout.decode().strip()
            
            checkout_cmd = f"git checkout {version}"
            run(checkout_cmd)
    
            run("pip3 install --upgrade -r requirements.txt")
    
            os.chdir(settings.BASE_DIR)
            run("python3 manage.py migrate")
            run("python3 manage.py collectstatic --no-input")
            run("python3 manage.py compilemessages")
        except subprocess.CalledProcessError as e:
            print(e)
            if e.stdout != None:
                print(f"stdout: {e.stdout}")
            if e.stderr != None:
                print(f"stderr:{e.stderr}")
