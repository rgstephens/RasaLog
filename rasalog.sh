#!/bin/sh
CUSTOMER=${1}
LOGFILE=${2}
echo python rasalog.py customers/${CUSTOMER}/${LOGFILE}.log \> customers/${CUSTOMER}/${LOGFILE}.md
python rasalog.py customers/${CUSTOMER}/${LOGFILE}.log > customers/${CUSTOMER}/${LOGFILE}.md