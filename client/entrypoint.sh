#!/bin/sh
# Replace environment variable placeholders
sed -i 's|%REACT_APP_BACKEND_HOST%|'"$REACT_APP_BACKEND_HOST"'|g' /usr/share/nginx/html/static/js/*.js
# Start nginx
exec "$@"