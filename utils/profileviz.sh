#!/bin/zsh
FILE=$1
gprof2dot -f pstats "$FILE" | dot -Tpng -o "${FILE%%.*}".png
snakeviz "$FILE"