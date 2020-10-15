cd src/components/ || exit;

for d in */; do
    cd "$d" || exit
    yarn build
    mkdir ../../"$d"
    cp -r "$d" ../../"$d"
    cd ..
done
