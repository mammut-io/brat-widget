import ipywidgets as widgets
from traitlets import Unicode


@widgets.register('brat.Visualizer')
class Visualizer(widgets.DOMWidget):
    """"""
    _view_name = Unicode('VisualizerView').tag(sync=True)
    _model_name = Unicode('VisualizerModel').tag(sync=True)
    _view_module = Unicode('brat-widget').tag(sync=True)
    _model_module = Unicode('brat-widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode('Hello Mammut 4!!!!').tag(sync=True)
