#!/bin/bash

pep8 solus_sc/*.py solus-sc || exit 1
flake8 solus_sc/*.py solus-sc || exit 1

