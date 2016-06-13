#!/bin/bash

pep8 solus_sc/*.py main.py || exit 1
flake8 solus_sc/*.py main.py || exit 1

