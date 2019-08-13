#!/bin/sh
./__env/bin/python3 yatranslate.py >> log.txt 2>&1 & echo $! >> log.pid
