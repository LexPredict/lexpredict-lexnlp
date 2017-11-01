#!/usr/bin/env bash
# Based on https://github.com/vaites/php-apache-tika

if [ "$LEXNLP_USE_TIKA" = true ]; then

PORT=9998
BINARIES=${APACHE_TIKA_BINARIES:-bin}
VERSION=${APACHE_TIKA_VERSION:-"1.16"}

RUNNING=`ps aux | grep -c tika-server-$VERSION`

if [ $RUNNING -lt 2 ]; then
    java -version
    echo "Starting Tika Server $VERSION"
    java -jar "$BINARIES/tika-server-$VERSION.jar" -p $PORT 2> /tmp/tika-server-$VERSION.log &
    ((PORT++))
    sleep 5
else
    echo "Tika Server $VERSION already running"
fi

fi