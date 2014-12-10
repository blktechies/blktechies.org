#! /usr/bin/env sh

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Create a very basic skeleton of a new sub-application" >&2
    echo "USAGE: $0 <subapp_name>" >&2
    exit
fi

APP_NAME="$1"
if [ -z "$APP_NAME" ]; then
    echo "You must specify a new app to create" >&2
    exit 1;
fi

ORIG_DIR="$( pwd )"

DIR="$( cd "$( dirname "$0" )" && pwd )"
cd "$DIR"/blacktechies/apps

if [ -e "$APP_NAME" ]; then
    echo "$APP_NAME already exists. Please remove it and re-run this script." >&2
    exit 2
fi

mkdir -p "$APP_NAME/templates" || exit 3

cd "$APP_NAME"
touch __init__.py models.py views.py || exit 4

cd "$ORIG_DIR"


    
   
