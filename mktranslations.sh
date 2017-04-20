#!/bin/bash

set -x
set -e

if [[ ! -d po ]]; then
    mkdir po
fi

grep "_(\"" */*.py|cut -d : -f 1 | uniq > list1
grep "_(\'" */*.py|cut -d : -f 1 | uniq > list2
cat list1 list2 > list3
# Merge xml files into final translations
for i in repo_data/*.xml.in; do
    echo "$i" >> list3
done
cat list3 | uniq | sort > po/POTFILES.in
rm list1 list2 list3

python2.7 setup.py build_i18n -m 
