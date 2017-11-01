#!/usr/bin/env bash
# Based on https://github.com/vaites/php-apache-tika

if [ "$LEXNLP_USE_TIKA" = true ]; then

BINARIES=${APACHE_TIKA_BINARIES:-bin}
VERSION=${APACHE_TIKA_VERSION:-"1.16"}
LATEST="1.16"

mkdir --parents $BINARIES

if [ $VERSION == $LATEST ]; then
   MIRROR="http://www-us.apache.org"
else
   MIRROR="https://archive.apache.org"
fi

if [ ! -f "$BINARIES/tika-app-$VERSION.jar" ]; then
    wget "$MIRROR/dist/tika/tika-app-$VERSION.jar" -O "$BINARIES/tika-app-$VERSION.jar"
fi

if [ ! -f "$BINARIES/tika-server-$VERSION.jar" ]; then
    wget "$MIRROR/dist/tika/tika-server-$VERSION.jar" -O "$BINARIES/tika-server-$VERSION.jar"
fi

fi
