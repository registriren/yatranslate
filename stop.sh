#!/bin/sh
    for j in `cat log.pid`
    do
      kill -9 ${j}
    done
    echo "$j is killed"
    rm log.pid
    cp log.txt log.$(date '+%s').txt
    rm log.txt
