#!/bin/sh
CUSTOMER=${1}
LOGFILE=${2}
python rasalog.py customers/${CUSTOMER}/${LOGFILE}.log > customers/${CUSTOMER}/${LOGFILE}.md 