#!/bin/bash

set -ex

#configuration
cp setup/setup_template.yml setup/setup_dev.yml

#proper environment
$(./mk_env_file.py)
$(./ch_dev_env.sh)

#virtual env for python
if [[ ! -d venv/ ]]; then
    python3 -m venv venv
fi
source venv/bin/activate

#packages
pip install -r ./requirements.txt

#fake db data generation, db init and population
mkdir -p data/
./gen_fake_data.py
./setup_db.sh --reset_db --create_su --su_passwd=rosquinha
./populate_db.sh

#tests
#./run_tests.sh

#server
./run_server.sh
