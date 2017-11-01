#!/usr/bin/env bash

if [ "$LEXNLP_USE_STANFORD" = true ]; then
echo "Stanford tests are enabled. Downloading stanford libs..."

# Set parameters
STANFORD_VERSION="2017-06-09"
STANFORD_PATH="libs/stanford_nlp"

# Download
wget --continue -O tmp.zip "http://nlp.stanford.edu/software/stanford-corenlp-full-$STANFORD_VERSION.zip"
unzip tmp.zip -d $STANFORD_PATH
rm -f tmp.zip

wget --continue -O tmp.zip "https://nlp.stanford.edu/software/stanford-parser-full-$STANFORD_VERSION.zip"
unzip tmp.zip -d $STANFORD_PATH
rm -f tmp.zip

wget --continue -O tmp.zip "https://nlp.stanford.edu/software/stanford-english-corenlp-$STANFORD_VERSION-models.jar"
unzip tmp.zip -d $STANFORD_PATH
rm -f tmp.zip

wget --continue -O tmp.zip "https://nlp.stanford.edu/software/stanford-postagger-full-$STANFORD_VERSION.zip"
unzip tmp.zip -d $STANFORD_PATH
rm -f tmp.zip

wget --continue -O tmp.zip "https://nlp.stanford.edu/software/stanford-ner-$STANFORD_VERSION.zip"
unzip tmp.zip -d $STANFORD_PATH
rm -f tmp.zip

ls -lh
ls -lh $STANFORD_PATH
fi

# Optional language-specific models
#wget "https://nlp.stanford.edu/software/stanford-french-corenlp-$STANFORD_VERSION-models.jar"
#wget "https://nlp.stanford.edu/software/stanford-german-corenlp-$STANFORD_VERSION-models.jar"
#wget "https://nlp.stanford.edu/software/stanford-spanish-corenlp-$STANFORD_VERSION-models.jar"
