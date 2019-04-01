#/usr/bin/env bash -e

config="./config.ini"
config_default="./config.ini.default"
if [ ! -f "$config" ]
then
    cp $config_default $config
fi

VENV=venv

if [ ! -d "$VENV" ]
then

    PYTHON=`which python3`

    if [ ! -f $PYTHON ]
    then
        echo "could not find python"
    fi
    virtualenv -p $PYTHON $VENV

fi

. $VENV/bin/activate

pip3 install --upgrade pip
pip3 install -r requirements.txt
pip3 install --upgrade hermes-python
