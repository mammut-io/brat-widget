$brat-widget
========

$brat-widget is a Jupiter Widget library for BRAT visualization and text annotation. This is an extension of original BRAT, 
an intuitive web-based tool for text annotation supported by Natural Language Processing (NLP) technology. 

Features
--------

- Comprehensive visualization
- Intuitive Annotation Interface
- High-quality Annotation Visualisation
- Always saved, always up to date
- Fully configurable
- NLP Technology Integration

Implementation
--------
BRAT has been developed for rich structured annotation for a variety of NLP tasks and aims to support manual curation 
efforts and increase annotator productivity using NLP techniques. 
$brat-widget is implemented using Jupyter Notebook technology with the intention of create and share documents that 
contain embedded code and execution results to help the annotators to gain skills on NLP and Corpus that they need. It has 
been implemented using a client-server architecture with communication over HTTP using JavaScript Object Notation (JSON). 
The server is a RESTful web service and the tool can easily be extended or adapted to switch out the server or client.

Installation
------------
For development purposes, you need [npm 3.10](https://www.npmjs.com/get-npm) and [node.js 6.11](https://nodejs.org/es/) installed, 
and some python packages than can be see it in the following list of steps using 
[virtualenv](https://virtualenv.pypa.io/en/latest/installation/) 
as package-enviroment manager.

Install $brat-widget by running:

```bash
virtualenv -p python3 env
source ./env/bin/activate
pip install jupyter
pip install jupyterlab
pip install jupyter_contrib_nbextensions
jupyter nbextension enable --py --sys-prefix widgetsnbextension
pip install nodejs
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

After these steps a small hack is necessary. 
You have to edit the file `js/webpack.config.js` by changing all the occurrences of the 
path `./brat-widget` for the exact location of this git project in your station.

The easiest way to star playing with the widget is using the reinit.sh script that is 
included in this project. Asuming that you have your virtualenv environment already activated 
(the second step in the list above `source ./env/bin/activate`), you have the following 
options:  
- `./reinit.sh -c`: clear all the npm installations made previously, prepare the 
					brad-widget python package from the scratch, and install it. 
- `./reinit.sh -s`: prepare the brad-widget python package (previously downloaded 
					javascript packages are reused), install it, and start jupyter 
					notebook.
- `./reinit.sh -s -c` or `./reinit.sh -sc`: clear all the npm installations made previously, 	
											prepare the brad-widget python package from the 
											scratch, install it, and start jupyter notebook.

Usage
----------

Once $brat-widget installed, a new browser window (or a new tab) is started showing the 
Notebook Dashboard.  A sort of control panel that allows (among other things) to select 
which notebook to open.

Now, you can navigate through web interface tree and select Notebooks folder. 
There in you can run the `Test.ipynb` notebook.

Additional actions can be performed:
	+ You can run the notebook document step-by-step (one cell a time) by pressing 
shift + enter.
	+ You can run the whole notebook in a single step by clicking 
	on the menu Cell -> Run All.
	+ To restart the kernel (i.e. the computational engine), click on 
	the menu Kernel -> Restart. 
	This can be useful to start over a computation from scratch
	
Packaging
----------

In order to generate a new package version and distribute it follow the next steps:
- Install Twine: `pip install twine`
- Packaging: 
    - Optional: git add and git commit
    - `jupyter labextension uninstall brat-widget`
    - `jupyter nbextension uninstall --sys-prefix brat_widget`
    - `pip uninstall -y brat-widget`
    - `./dev-clean.sh`
    - `python setup.py build`
    - `cp -r ./js/brat_widget/static ./brat_widget/`
    - `python setup.py sdist`
    - `python setup.py bdist_wheel`
    - Check description: 
        - `pip install readme_renderer`
        - `twine check dist/*`
    - Upload distribution: `twine upload dist/*`
    - Upload to npm:
        - `pushd js`
        - `git clean -fdx`
        - `npm install`
        - `npm pack`
        - Optional: `npm adduser`
        - `npm publish`
        - `popd`
    - Optional: update _version.py (add 'dev' and increment minor)
    - Optional: git add and git commit
    - Optional: `git tag -a 0.2.4 -m "comment"`
    - Optional: `git push`
    - Optional: `git push --tags`

Contribute
----------

- Issue Tracker: https://github.com/Edilmo/brat-widget/issues
- Source Code: https://github.com/Edilmo/brat-widget.git

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: [support@mammut.io](mailto:support@mammut.io)

License
-------

The project is licensed under the BSD license.