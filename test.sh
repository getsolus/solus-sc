#!/bin/bash

pep8 test/*.py || exit 1

python test/updates_parse.py
