p#!/bin/bash

rm -rf venv
python3 -m venv venv
source venv/bin/activate
venv/bin/pip install --upgrade setuptools pip wheel
venv/bin/pip install -r requirements.txt
