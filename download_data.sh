#!/bin/bash
URL="https://data.cityofnewyork.us/api/views/qgea-i56i/rows.csv?accessType=DOWNLOAD"
FILENAME="data.csv"

if [ ! -f "$FILENAME" ]; then
    echo "Downloading data..."
    curl -L "$URL" -o "$FILENAME"
    echo "Done."
else
    echo "$FILENAME already exists."
fi
