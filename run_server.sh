#!/bin/bash

[[ -z $NEWVALLEY_ENV ]] && app_env='development' || app_env=$NEWVALLEY_ENV
[[ -z $NEWVALLEY_HOST ]] && host='localhost' || host=$NEWVALLEY_HOST
[[ -z $NEWVALLEY_PORT ]] && port=5000 || port=$NEWVALLEY_PORT
export FLASK_APP=nv.app:get_app
export FLASK_ENV=$app_env
flask run --host=$host --port=$port $@
