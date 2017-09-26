#!/bin/bash

pep8 solus_sc/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1
flake8 --builtins="_" solus_sc/*.py solus_update/*.py solus-sc solus-update-checker eopkg_assist/*.py || exit 1

# Now for our staging tree

pep8 snapTests/*-* snapTests/plugins/*.py || exit 1
flake8 --builtins="_" snapTests/*-* snapTests/plugins/*.py || exit 1

