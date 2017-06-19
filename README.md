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
    conda create -n brat-36 python=3.6
    source activate brat-36
    git clone https://github.com/Edilmo/brat-widget.git
    cd brat-widget
    pip install -e .
    jupyter nbextension install --py --symlink --sys-prefix brat_widget
    jupyter nbextension enable --py --sys-prefix brat_widget
```
