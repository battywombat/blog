#!/bin/bash

export FLASK_APP=`readlink -f ./__init__.py`
export FLASK_DEBUG=1
flask run --host=0.0.0.0
