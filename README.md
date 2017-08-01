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

## Notes of the adaptation:

- The regex `\$\('#([a-zA-Z_0-9\-]+)'\)` was used to find all the calls to JQuery that look for a specific element in the DOM. And the regex `\$\('#' \+ base_id \+ '_$1'\)` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `\$\('#' \+ base_id \+ '_([a-zA-Z_0-9\-]+)'\)`.
- The regex `id="([a-zA-Z_0-9\-]+)"` was used to find all the ids in the brat DOM embedded in the widget. And the regex `id="\{base_id\}_$1"` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `id="\{base_id\}_([a-zA-Z_0-9\-]+)"`.
- The regex `for="([a-zA-Z_0-9\-]+)"` was used to find all the referenced ids in the brat DOM embedded in the widget. And the regex `for="\{base_id\}_$1"` was used to perform the replacement using PyCharm. To find all the replacements use the following regex: `for="\{base_id\}_([a-zA-Z_0-9\-]+)"`.
- The regex `\$\('#([a-zA-Z_ \.:-\[\]\(\)0-9\-]+)'\)` was used to find all the calls to JQuery that look for a path of several elements in the DOM. The result of this lookup gave 49 occurences in two files. The regex `\$\('#([a-zA-Z_\.:-\[\]\(\)0-9\-]+) ` was used as the lookup expression and `\$\('#' \+ base_id \+ '_$1 ` was used to perform the replacement using PyCharm. The regexes showed before produce more results than the first global lookup expression. To find all the replacements use the following regex: `\$\('#' \+ base_id \+ '_([a-zA-Z_]+) `. After the following was used to select another specific cases `#([a-zA-Z_\.:-\[\]\(\)0-9\-]+)`and `#' \+ base_id \+ '_$1` was used to perform the replacement using PyCharm.
- In order to find the remaining cases where a DOM element is constructed using jQuery, the following regex was used to lookup `(id|for)="([a-zA-Z_0-9\-]+)` and this `$1="' \+ base_id \+ '_$2` was used for replacement.

## Examples of the JSON documents sent to the server:

- [Span actions](http://www.jsoneditoronline.org/?id=c11d7be261c2f507f15ea9733e927d38)
- [Arc actions](http://www.jsoneditoronline.org/?id=dcac7fd71ec6f3716ba9f0265cb399ff)
- [Other actions](http://www.jsoneditoronline.org/?id=dcac7fd71ec6f3716ba9f0265cbc464a)
