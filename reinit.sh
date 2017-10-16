#!/usr/bin/env bash

jupyter nbextension uninstall --sys-prefix brat_widget

pip uninstall -y brat-widget

if [ "$1" == "-c" ] || [ "$2" == "-c" ] || [ "$1" == "-sc" ] || [ "$1" == "-cs" ]; then
    echo "Cleaning environment..."
    ./dev-clean.sh
    echo "Environment clean"
else
    echo "The environment has not been cleaned"
fi

#read -r
pip install -e .

jupyter nbextension install --py --sys-prefix brat_widget
jupyter nbextension enable --py --sys-prefix brat_widget
if [ "$1" == "-s" ] || [ "$2" == "-s" ] || [ "$1" == "-sc" ] || [ "$1" == "-cs" ]; then
    jupyter notebook
fi
