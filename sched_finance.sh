#!/bin/bash -e

BASEDIR=`dirname $0`

source $BASEDIR/ve/bin/activate
cd $BASEDIR
export PYTHONPATH=$PYTHONPATH:.

exec python $BASEDIR/fooltrader/sched/sched_quote.py
