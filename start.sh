#!/bin/sh
python3.6 yatranslate.py >> log.txt 2>&1 & echo $! >> log.pid
