#!/bin/bash -e

BASEDIR=`dirname $0`

if ! which python3 > /dev/null; then
   echo -e "Python3 not found! Install? (y/n) \c"
   read
   if [ "$REPLY" = "y" ]; then
      sudo apt-get install python3
   fi
fi

if ! which virtualenv > /dev/null; then
   echo -e "virtualenv not found! Install? (y/n) \c"
   read
   if [ "$REPLY" = "y" ]; then
      sudo apt-get install python-virtualenv
   fi
fi

if [ ! -d "$BASEDIR/ve" ]; then
    virtualenv -p python3 $BASEDIR/ve --system-site-packages
    echo "Virtualenv created."
fi

source $BASEDIR/ve/bin/activate
cd $BASEDIR
export PYTHONPATH=$PYTHONPATH:.

if [ ! -f "$BASEDIR/ve/updated" -o $BASEDIR/requirements.txt -nt $BASEDIR/ve/updated ]; then
    pip install -r $BASEDIR/requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
    touch $BASEDIR/ve/updated
    echo "Requirements installed."
fi

echo $BASEDIR
exec python $BASEDIR/fooltrader/main.py
