#!/usr/bin/env bash
# Path
WIKI_PATH="wiki"

mkdir -p $WIKI_PATH
wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2 -O "$WIKI_PATH/en.xml.bz2"
wget https://dumps.wikimedia.org/eswiki/latest/eswiki-latest-pages-articles-multistream.xml.bz2 -O "$WIKI_PATH/es.xml.bz2"
#wget https://dumps.wikimedia.org/dewiki/latest/frwiki-latest-pages-articles-multistream.xml.bz2 -O "$WIKI_PATH/fr.xml.bz2"
#wget https://dumps.wikimedia.org/frwiki/latest/dewiki-latest-pages-articles-multistream.xml.bz2 -O "$WIKI_PATH/de.xml.bz2"
