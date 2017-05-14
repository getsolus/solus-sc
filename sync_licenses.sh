#!/bin/bash

fail_exit(){
    echo "$1"
    exit 1
}

git clone https://github.com/spdx/license-list.git --depth=1 || fail_exit "Failed to clone"

if [[ -e "licenses.spdx" ]];
    then rm -v licenses.spdx
fi

pushd license-list

echo "licenses = [" > ../licenses.spdx
for i in *.txt ; do
    nom=`echo "$i" | sed 's@\.txt$@@'`
    echo -e "    \"${nom}\"," >> ../licenses.spdx
done
popd
rm -rf license-list
echo "]" >> licenses.spdx
