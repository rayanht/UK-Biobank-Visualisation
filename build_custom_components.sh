#!/usr/bin/env bash
cd custom_components/ || exit;

for d in */; do
    cd "$d" || exit
    yarn install
    yarn build
    mkdir ../../src/"$d"
    cp -r "$d" ../../src/"$d"
    cd ..
done
