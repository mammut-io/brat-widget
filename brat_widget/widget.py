import ipywidgets as widgets
from traitlets import Unicode, Dict, Instance
import json

class GeneralVisualConfiguration:
    def __init__(self):
        self.marginX = 2
        self.marginY = 1
        self.arcTextMargin = 1
        self.boxSpacing = 1
        self.curlyHeight = 4
        self.arcSpacing = 9 # 10
        self.arcStartHeight = 19 # 23 # 25

    def get_dict(self):
        return {
            'margin': {
                'x': self.marginX,
                'y': self.marginY
            },
            'arcTextMargin': self.arcTextMargin,
            'boxSpacing': self.boxSpacing,
            'curlyHeight': self.curlyHeight,
            'arcSpacing': self.arcSpacing,
            'arcStartHeight': self.arcStartHeight
        }

    def set_from_dict(self, dict):
        self.marginX = dict['margin']['x']
        self.marginY = dict['margin']['y']
        self.arcTextMargin = dict['arcTextMargin']
        self.boxSpacing = dict['boxSpacing']
        self.curlyHeight = dict['curlyHeight']
        self.arcSpacing = dict['arcSpacing']
        self.arcStartHeight = dict['arcStartHeight']


class GeneralConfiguration:
    def __init__(self):
        self.abbrevsOn = True
        self.textBackgrounds = "striped"
        self.svgWidth = '100%'
        self.rapidModeOn = False
        self.confirmModeOn = True
        self.autorefreshOn = False
        self.typeCollapseLimit = 30
        self.visual = GeneralVisualConfiguration()

    def get_dict(self):
        return {
            'abbrevsOn': self.abbrevsOn,
            'textBackgrounds': self.textBackgrounds,
            'svgWidth': self.svgWidth,
            'rapidModeOn': self.rapidModeOn,
            'confirmModeOn': self.confirmModeOn,
            'autorefreshOn': self.autorefreshOn,
            'typeCollapseLimit': self.typeCollapseLimit,
            'visual': self.visual.get_dict()
        }

    def set_from_dict(self, dict):
        self.abbrevsOn = dict['abbrevsOn']
        self.textBackgrounds = dict['textBackgrounds']
        self.svgWidth = dict['svgWidth']
        self.rapidModeOn = dict['rapidModeOn']
        self.confirmModeOn = dict['confirmModeOn']
        self.autorefreshOn = dict['autorefreshOn']
        self.typeCollapseLimit = dict['typeCollapseLimit']
        self.visual.set_from_dict(dict['visual'])

    @classmethod
    def to_json(cls, conf, widget_model):
        return json.dumps(conf.get_dict())

    @classmethod
    def from_json(cls, json_str, widget_model):
        dict = json.loads(json_str)
        res = GeneralConfiguration()
        res.set_from_dict(dict)
        return res


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
    general_configuration = Instance(klass=GeneralConfiguration,
                                     default_value=GeneralConfiguration()).tag(sync=True,
                                                                               to_json=GeneralConfiguration.to_json,
                                                                               from_json=GeneralConfiguration.from_json)
