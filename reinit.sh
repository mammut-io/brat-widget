#!/usr/bin/env bash

set -ex

if [ "$1" == "-c" ] || [ "$2" == "-c" ] || [ "$1" == "-sc" ] || [ "$1" == "-cs" ]; then
    echo "Cleaning environment..."
    ./dev-clean.sh
    echo "Environment clean"
else
    echo "The environment has not been cleaned"
fi

pip install -e .

jupyter nbextension install --py --symlink --sys-prefix brat_widget
jupyter nbextension enable --py --sys-prefix brat_widget
if [ "$1" == "-d" ] || [ "$2" == "-d" ] || [ "$1" == "-dc" ] || [ "$1" == "-ds" ]; then
  jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
  jupyter labextension link ./js
  pushd js && npm run watch
else
  python setup.py build
  jupyter labextension install @jupyter-widgets/jupyterlab-manager
  jupyter labextension install ./js
  if [ "$1" == "-s" ] || [ "$2" == "-s" ] || [ "$1" == "-sc" ] || [ "$1" == "-cs" ]; then
      jupyter lab
  fi
fi
