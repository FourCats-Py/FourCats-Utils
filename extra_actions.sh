#!/bin/bash
# shellcheck disable=SC2124
params=${@:2}
baseName=$(basename "$1")

function changeVersion() {
  if [[ "$baseName" =~ "beta" ]]; then
    version=$(echo "$baseName" | grep -E "^v[0-9]+.[0-9]+.[0-9]+-beta.[0-9]+$")
  else
    version=$(echo "$baseName" | grep -E "^v[0-9]+.[0-9]+.[0-9]+$")
  fi

  if [[ "$version" == "" ]]; then
    echo "No version number matched."
    exit 1
  fi

  version=${version:1}
  echo ::set-output name=version::"$version"

  echo "Get version $version"

  sed -i -r "s/^__version__[[:space:]]+=[[:space:]]+[\'\"](.*)[\'\"]$/__version__ = \"$version\"/" fourcats_utils/__init__.py

  cat fourcats_utils/__init__.py

}

function releasePack() {
  cd ..
  newDirName="FourCats-Utils-$version"
  tarName="FourCats-Utils-$version.tar.gz"
  zipName="FourCats-Utils-$version.zip"

  cp -r ./FourCats-Utils ./"$newDirName"

  tar -zcvf "$tarName" ./"$newDirName"
  zip -r -q "$zipName" ./"$newDirName"

  cp "$tarName" ./FourCats-Utils/"$tarName"
  cp "$zipName" ./FourCats-Utils/"$zipName"

  echo ::set-output name=tarName::"$tarName"
  echo ::set-output name=zipName::"$zipName"
}

function main() {
  for key in $params; do
    if [[ $key == "changeVersion" ]]; then
      changeVersion
    elif [[ $key == "releasePack" ]]; then
      releasePack
    else
      echo "$key"
    fi
  done
}

main