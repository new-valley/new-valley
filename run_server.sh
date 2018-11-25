#!/bin/bash

[[ -z $NEWVALLEY_ENV ]] && app_env='development' || app_env=$NEWVALLEY_ENV
[[ -z $NEWVALLEY_HOST ]] && host='localhost' || host=$NEWVALLEY_HOST
[[ -z $NEWVALLEY_PORT ]] && port=5000 || port=$NEWVALLEY_PORT
[[ -z $NEWVALLEY_N_WORKERS ]] && n_workers=1 || n_workers=$NEWVALLEY_N_WORKERS

export FLASK_APP=nv.app:get_app
export FLASK_ENV=$app_env

if [[ "$app_env" == 'development' ]]; then
    flask run --host=$host --with-threads --port=$port $@
else
    gunicorn -w $n_workers -b "$host:$port" 'nv.app:get_app()' $@
fi
