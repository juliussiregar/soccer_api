import argparse
import random
import subprocess
import sys
import time
import logging
logging.getLogger().setLevel(logging.INFO)

parser = argparse.ArgumentParser(description='alembic migration script.')
parser.add_argument('--message', '-m', required=True, help='Migration message.')
parser.add_argument('--run', action='store_true', help='Also run the migration after generating migration script.')
args = parser.parse_args()

sys.path.append('')

from alembic.config import Config
from alembic import command

docker_name = f'postgres_{random.randint(10000, 99999)}'
postgres_port = random.randint(8000, 10000)
postgres_port = 5432
print('Starting postgres container.')
subprocess.call(f'docker run --name {docker_name} -e POSTGRES_USER=solidPace1 -e POSTGRES_PASSWORD=solidPace1!1! -e POSTGRES_DB=solidPace1 -d -p 127.0.0.1:{postgres_port}:5432 timescale/timescaledb:latest-pg12', shell=True)

try:
    time.sleep(30)
    alembic_cfg = Config('alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', f'postgresql+psycopg2://solidPace1:solidPace1@127.0.0.1:{postgres_port}/solidPace1')
    alembic_cfg.set_main_option('script_location', 'alembic')
    print('Upgrading postgres to recent migrations.')
    command.upgrade(alembic_cfg, "head")
    print('Generating migration scripts.')
    command.revision(alembic_cfg, args.message, autogenerate=True)
    if args.run:
        print('Running migration script.')
        command.upgrade(alembic_cfg, "head")
finally:
    print('Removing postgres container.')
    subprocess.call(f'docker container stop {docker_name}', shell=True)
    subprocess.call(f'docker container rm {docker_name}', shell=True)
    print('Done.')
