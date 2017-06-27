import ipywidgets as widgets
from traitlets import Unicode, Dict


@widgets.register('brat.Visualizer')
class Visualizer(widgets.DOMWidget):
    """"""
    _view_name = Unicode('VisualizerView').tag(sync=True)
    _model_name = Unicode('VisualizerModel').tag(sync=True)
    _view_module = Unicode('brat-widget').tag(sync=True)
    _model_module = Unicode('brat-widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Dict().tag(sync=True)
    collection = Dict().tag(sync=True)

@widgets.register('brat.Annotator')
class Annotator(Visualizer):
    """"""
    _view_name = Unicode('AnnotatorView').tag(sync=True)
    _model_name = Unicode('AnnotatorModel').tag(sync=True)
    _view_module = Unicode('brat-widget').tag(sync=True)
    _model_module = Unicode('brat-widget').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
