#!/usr/bin/env bash

set -e

BIN_PATH=''
SHARE_PATH='~/.local/share/pocket'
CONFIG_PATH='~/.config/pocket'

if [[ $PATH == '' ]]; then
    BIN_PATH='~/.local/bin'
else
    BIN_PATH=$(echo "$PATH" | cut -d':' -f1)
fi

echo "installing to: $BIN_PATH/pocket"
echo -n 'OK? [yes/no] '
read OK

if [[ $OK != 'yes' ]]; then
    echo -n "type alternative installation path: "
    read BIN_PATH
fi

echo "installing to: $BIN_PATH/pocket"

# Install executable
mkdir -p $BIN_PATH
cp ./pocket.py $BIN_PATH/pocket

# Install interface definition
mkdir -p $SHARE_PATH
cp ./ui.json $SHARE_PATH/ui.json

# Create config directory
mkdir -p ~/.config/pocket
