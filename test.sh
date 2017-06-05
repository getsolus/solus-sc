#!/bin/bash

pep8 solus_sc/*.py solus_sc20/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1
flake8 --builtins="_" solus_sc/*.py solus_sc20/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1

