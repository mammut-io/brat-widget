# brat-widget

Jupiter Widget library for BRAT visualization and annotation functionality.

## Installation

To install use pip:
```bash
    pip install brat_widget
    jupyter nbextension enable --py --sys-prefix brat_widget
```


For a development installation (requires npm),
```bash
    npm install cucumber
    npm install requirejs
    npm install jasmine-core
    npm install jasmine
    npm install ajv
    npm install karma
    npm install webpack@2.2.0
    npm install karma-webpack
    npm install karma-jasmine
    npm install karma-chrome-launcher
    npm install karma-requirejs
    npm install -g karma-cli
    conda create -n brat-27 python=2.7
    source activate brat-27
    conda install jupyter
    conda install -c conda-forge jupyter_contrib_nbextensions
    conda install nb_conda_kernels
    conda install widgetsnbextension
    conda install ipywidgets
    jupyter nbextension enable --py --sys-prefix widgetsnbextension
    git clone https://github.com/Edilmo/brat-widget.git
    cd brat-widget
    ln -s ../../brat/client/src/ js/src/brat
    ln -s ../../brat/client/lib/ js/src/lib
    ln -s ../../brat/static js/src/static
    pip install -e .
    jupyter nbextension install --py --sys-prefix brat_widget
    jupyter nbextension enable --py --sys-prefix brat_widget
    jupyter notebook
    jupyter nbextension uninstall --sys-prefix brat_widget
    pip uninstall brat-widget
    ./dev-clean.sh
```
