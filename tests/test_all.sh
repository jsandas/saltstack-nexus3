#!/bin/sh

for file in $(ls *.py)
do
    echo ""
    echo "Running $file..."
    ./$file
    echo ""
done