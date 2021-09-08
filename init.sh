#!/usr/bin/env sh
python -m venv venv
if [[ -d venv/bin ]]; then
source venv/bin/activate
elif [[ -d venv/Scripts ]]; then
source venv/Scripts/activate
else
	echo "Activation script not found in venv, aborting..."
	exit
fi
pip install -r requirements.txt
