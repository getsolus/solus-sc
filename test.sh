#!/bin/bash

pep8 solus_sc/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1
flake8 solus_sc/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1

