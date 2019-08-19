#!/usr/bin/env bash

jupyter labextension uninstall brat-widget
jupyter nbextension uninstall --sys-prefix brat_widget
jupyter labextension uninstall @jupyter-widgets/jupyterlab-manager
jupyter lab clean
pip uninstall -y brat-widget

pushd ./js
npm run clean
popd

rm -f ./js/package-lock.json
rm -f ./js/brat-widget-*.tgz
rm -f brat_widget/brat-widget-*.tgz
rm -rf ./js/dist/
rm -rf ./js/node_modules/
rm -rf ./js/brat_widget/
rm -f ./brat_widget/yarn.lock
rm -rf ./brat_widget/static/
rm -rf ./brat_widget/node_modules/
rm -rf ./build/
rm -rf ./dist/
rm -rf ./brat_widget.egg-info/
