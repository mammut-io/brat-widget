import ipywidgets as widgets
from traitlets import Unicode, Dict, Instance

from brat_widget.common import ProtocolError
from brat_widget.configuration import GeneralConfiguration, CollectionConfiguration
from brat_widget.document import Document
from brat_widget.messager import Messager

from ._version import __frontend_version__

@widgets.register('brat.Visualizer')
class Visualizer(widgets.DOMWidget):
    """"""
    _view_name = Unicode('VisualizerView').tag(sync=True)
    _model_name = Unicode('VisualizerModel').tag(sync=True)
    _view_module = Unicode('brat-widget').tag(sync=True)
    _model_module = Unicode('brat-widget').tag(sync=True)
    _view_module_version = Unicode(__frontend_version__).tag(sync=True)
    _model_module_version = Unicode(__frontend_version__).tag(sync=True)
    value = Instance(klass=Document,default_value=Document()).tag(sync=True,
                                                                  to_json=Document.to_json,
                                                                  from_json=Document.from_json)
    collection_configuration = Instance(klass=CollectionConfiguration,
                                     default_value=CollectionConfiguration()).tag(sync=True,
                                                                               to_json=CollectionConfiguration.to_json,
                                                                               from_json=CollectionConfiguration.from_json)
    # value = Dict().tag(sync=True)
    # collection_configuration = Dict().tag(sync=True)

@widgets.register('brat.Annotator')
class Annotator(Visualizer):
    """"""
    def __init__(self, **kwargs):
        def local_custom_message_handler(widget, content, buffers):
            self._custom_message_handler(widget, content, buffers)

        super(Visualizer, self).__init__(**kwargs)
        self.on_msg(local_custom_message_handler)

    _view_name = Unicode('AnnotatorView').tag(sync=True)
    _model_name = Unicode('AnnotatorModel').tag(sync=True)
    _view_module = Unicode('brat-widget').tag(sync=True)
    _model_module = Unicode('brat-widget').tag(sync=True)
    _view_module_version = Unicode(__frontend_version__).tag(sync=True)
    _model_module_version = Unicode(__frontend_version__).tag(sync=True)
    general_configuration = Instance(klass=GeneralConfiguration,
                                     default_value=GeneralConfiguration()).tag(sync=True,
                                                                               to_json=GeneralConfiguration.to_json,
                                                                               from_json=GeneralConfiguration.from_json)

    def _get_action_executor(self, action):
        def createSpan(data):
            return self.value.create_span(data)

        def deleteSpan(data):
            return self.value.delete_span(data['id'])

        def createArc(data):
            return self.value.create_arc(data)

        def deleteArc(data):
            return self.value.delete_arc(data['origin'], data['target'], data['type'])

        executor = None
        if action == 'createSpan':
            executor = createSpan
        elif action == 'deleteSpan':
            executor = deleteSpan
        elif action == 'createArc':
            executor = createArc
        elif action == 'deleteArc':
            executor = deleteArc
        return executor

    def _custom_message_handler(self, widget, content, buffers):
        content_dict = content
        action = content_dict['data']['action']
        current_id = content_dict['id']
        executor = self._get_action_executor(action)
        response = {'action': action}
        response_dict = {
            'action': action,
            'id': current_id,
            'success': True
        }
        if executor:
            try:
                response.update(executor(content_dict['data']))
            except ProtocolError as pe:
                print('Error: ' + str(pe))
                pe.json(response)
            except Exception as e:
                print('Error: ' + str(e))
                response['exception'] = 'Unexpected exception: ' + str(e)
        else:
            response['statusText'] = 'Not supported action.'
            #This was inherited from the original brat implementation. It was used to handle the ajax errors
            response_dict['success'] = False
            response_dict['textStatus'] = 'Not supported action ' + action
            response_dict['errorThrown'] = ''
        Messager.output_json(response)
        response_dict['response'] = response
        self.send(response_dict)
