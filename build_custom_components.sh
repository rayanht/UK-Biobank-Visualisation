#!/usr/bin/env bash
cd custom_components/ || exit;

for d in */; do
    cd "$d" || exit
    yarn install
    yarn build
    mkdir ../../"$d"
    cp -r "$d" ../../"$d"
    cd ..
done
