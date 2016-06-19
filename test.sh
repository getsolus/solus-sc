#!/bin/bash

pep8 solus_sc/*.py solus-sc eopkg_assist/*.py || exit 1
flake8 solus_sc/*.py solus-sc eopkg_assist/*.py || exit 1

