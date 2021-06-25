#!/usr/bin/env bash
# encode story.txt
time python huffman.py -e story.txt -o story_huff.txt
# decode story.txt
time python huffman.py -d story_huff.txt -o story_.txt
# find differences
./diff.sh story.txt story_.txt
#find compression ratio
echo "Compression ratio"
expr $(ls -l story.txt | awk '{ print $5 }')/$(ls -l story_huff.txt | awk '{ print $5 }') | bc -l
sleep 30