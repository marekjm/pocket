#!/usr/bin/env bash

set -e

BIN_PATH=$1
SHARE_PATH='~/.local/share/pocket'
CONFIG_PATH='~/.config/pocket'

if [[ $BIN_PATH == '' ]]; then
    BIN_PATH=$(echo "$PATH" | cut -d':' -f1)
fi

echo "installing to: $BIN_PATH/pocket"
echo -n 'OK? [yes/no] '
read OK

if [[ $OK != 'yes' ]]; then
    echo -n "type alternative installation path: "
    read BIN_PATH
    echo "installing to: $BIN_PATH/pocket"
fi

# Install executable
mkdir -p $BIN_PATH
cp ./pocket.py $BIN_PATH/pocket

# Install interface definition
mkdir -p $SHARE_PATH
cp ./ui.json $SHARE_PATH/ui.json

# Create config directory
mkdir -p ~/.config/pocket
