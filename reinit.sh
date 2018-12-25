#!/usr/bin/env bash

jupyter labextension uninstall brat-widget

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
python setup.py build
cp -r ./js/brat_widget/static ./brat_widget/
pip install -e .

jupyter nbextension install --py --sys-prefix brat_widget
jupyter nbextension enable --py --sys-prefix brat_widget
jupyter labextension install ./js/
if [ "$1" == "-s" ] || [ "$2" == "-s" ] || [ "$1" == "-sc" ] || [ "$1" == "-cs" ]; then
    jupyter lab
fi
