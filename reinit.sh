#!/usr/bin/env bash

jupyter nbextension uninstall --sys-prefix brat_widget
pip uninstall brat-widget
dev-clean
pip install -e .
jupyter nbextension install --py --sys-prefix brat_widget
jupyter nbextension enable --py --sys-prefix brat_widget
jupyter notebook