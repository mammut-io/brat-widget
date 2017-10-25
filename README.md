# brat-widget

Jupiter Widget library for BRAT visualization and annotation functionality.

## Installation

For development you need [npm 3.10 and node.js 6.11](https://www.npmjs.com/get-npm) installed, and some python packages than can be see it in the following list of steps that use [conda](https://conda.io/docs/user-guide/install/index.html#regular-installation) as package-enviroment manager.
```bash
    conda create -n brat-36 python=3.6
    source activate brat-36
    conda install jupyter
    conda install -c conda-forge jupyter_contrib_nbextensions
    conda install nb_conda_kernels
    conda install widgetsnbextension
    conda install ipywidgets
    jupyter nbextension enable --py --sys-prefix widgetsnbextension
    git clone https://github.com/Edilmo/brat-widget.git
    cd brat-widget
```
After these steps a small hack is necessary. You need to edit the file `js/webpack.config.js` by changing all the occurrences of the path `/Users/Edilmo/git/brat-widget` for the exact location of this git project in your machine.

The easiest way to star playing with the widget is using the reinit.sh script that is included in this project. Asuming that you have your conda environment already activated (the second step in the list above `source activate brat-36`), you have the following options:  
- `./reinit.sh -c`: clear all the npm installations made previously, prepare the brad-widget python package from the scrash, and install it. 
- `./reinit.sh -s`: prepare the brad-widget python package (previously downloaded javascript packages are reused), install it, and start jupyter notebook.
- `./reinit.sh -s -c` or `./reinit.sh -sc`: clear all the npm installations made previously, prepare the brad-widget python package from the scrash, install it, and start jupyter notebook.

