# coding=utf-8
import unittest
import json

from brat_widget.messager import Messager
from brat_widget.widget import Visualizer, Annotator
from brat_widget.configuration import CollectionConfiguration, GeneralConfiguration
from brat_widget.document import Document


class DocumentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.just_entities_collection_configuration = CollectionConfiguration()
        cls.just_entities_collection_configuration.entity_types = [{
            'type': 'Person',
            # The labels are used when displaying the annotion, in this case
            # we also provide a short-hand "Per" for cases where
            # abbreviations are preferable
            'labels': ['Person', 'Per'],
            # Blue is a nice colour for a person?
            'bgColor': '#7fa2ff',
            # Use a slightly darker version of the bgColor for the border
            'borderColor': 'darken'
        }]
        cls.just_entities_collection_configuration.initialize()

        cls.entities_relations_and_events_collection_configuration = CollectionConfiguration()
        cls.entities_relations_and_events_collection_configuration.entity_types = [{
            "type": "Person",
            "labels": ["Person", "Per"],
            "bgColor": "#7fa2ff",
            'attributes': [u'Notorious'],
            "borderColor": "darken"
        }]
        cls.entities_relations_and_events_collection_configuration.entity_attribute_types = [{
            "type": "Notorious",
            "values": {
                "Notorious": {"glyph": "★"}
            },
            "bool": "Notorious"
        }]
        cls.entities_relations_and_events_collection_configuration.relation_types = [{
            "type": "Anaphora",
            "labels": ["Anaphora", "Ana"],
            "dashArray": "3,3",
            "color": "purple",
            "args": [{
                "role": "Anaphor",
                "targets": ["Person"]
            }, {
                "role": "Entity",
                "targets": ["Person"]
            }]
        }]
        cls.entities_relations_and_events_collection_configuration.event_types = [{
            "type": "Assassination",
            "labels": ["Assassination", "Assas"],
            "bgColor": "lightgreen",
            "borderColor": "darken",
            "arcs": [{
                "type": "Victim",
                "labels": ["Victim", "Vict"],
                'targets': [u'<ANY>']
            }, {
                "type": "Perpetrator",
                "labels": ["Perpetrator", "Perp"],
                "color": "green",
                'targets': [u'<ANY>']
            }]
        }]
        cls.entities_relations_and_events_collection_configuration.initialize()

        cls.full_collection_configuration = CollectionConfiguration()
        cls.full_collection_configuration.description = None
        cls.full_collection_configuration.disambiguator_config = []
        cls.full_collection_configuration.entity_attribute_types = [
            {
                'unused': False,
                'values': [{'dashArray': u',', 'name': u'Individual',
                            'glyph': u'(I)'}],
                'labels': None,
                'type': u'Individual',
                'name': u'Individual'},
            {
                'unused': False,
                'values': [{'position': u'left', 'dashArray': u',',
                            'name': u'Name', 'glyph': u'(N)'},
                           {'position': u'left', 'dashArray': u',',
                            'name': u'Nominal', 'glyph': u'(n)'},
                           {'position': u'left', 'dashArray': u',',
                            'name': u'Other', 'glyph': u'(o)'}],
                'labels': None,
                'type': u'Mention',
                'name': u'Mention'}]
        cls.full_collection_configuration.event_types = [
            {'borderColor': u'darken',
             'normalizations': [],
             'name': u'Life',
             'labels': None,
             'children': [
                 {'borderColor': u'darken',
                  'normalizations': [],
                  'name': u'Be born',
                  'arcs': [{'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'name': u'Person',
                            'labels': [u'Person'],
                            'dashArray': u',',
                            'type': u'Person-Arg',
                            'count': '{1-5}',  # '{2}', '', '?', '*', '+'
                            'targets': [u'Person']},
                           {'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Place'],
                            'dashArray': u',',
                            'type': u'Place-Arg',
                            'targets': [u'GPE']}],
                  'labels': [u'Be born'],
                  'children': [],
                  'unused': False,
                  'bgColor': u'lightgreen',
                  'attributes': ['Negation', u'Confidence'],
                  'type': u'Be-born',
                  'fgColor': u'black'},
                 {'borderColor': u'darken',
                  'normalizations': [],
                  'name': u'Marry',
                  'arcs': [{'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Person'],
                            'dashArray': u',',
                            'type': u'Person-Arg',
                            'targets': [u'Person']},
                           {'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Place'],
                            'dashArray': u',',
                            'type': u'Place-Arg',
                            'targets': [u'GPE']}],
                  'labels': None,
                  'children': [],
                  'unused': False,
                  'bgColor': u'lightgreen',
                  'attributes': ['Negation', u'Confidence'],
                  'type': u'Marry',
                  'fgColor': u'black'},
                 {'borderColor': u'darken',
                  'normalizations': [],
                  'name': u'Divorce',
                  'arcs': [{'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Person'],
                            'dashArray': u',',
                            'type': u'Person-Arg',
                            'targets': [u'Person']},
                           {'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Place'],
                            'dashArray': u',',
                            'type': u'Place-Arg',
                            'targets': [u'GPE']}],
                  'labels': None,
                  'children': [],
                  'unused': False,
                  'bgColor': u'lightgreen',
                  'attributes': ['Negation', u'Confidence'],
                  'type': u'Divorce',
                  'fgColor': u'black'},
                 {'borderColor': u'darken',
                  'normalizations': [],
                  'name': u'Die',
                  'arcs': [{'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Person'],
                            'dashArray': u',',
                            'type': u'Person-Arg',
                            'targets': [u'Person']},
                           {'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Agent'],
                            'dashArray': u',',
                            'type': u'Agent-Arg',
                            'targets': [u'Person',
                                        u'Organization',
                                        u'GPE']},
                           {'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black',
                            'labels': [u'Place'],
                            'dashArray': u',',
                            'type': u'Place-Arg',
                            'targets': [u'GPE']}],
                  'labels': None,
                  'children': [],
                  'unused': False,
                  'bgColor': u'lightgreen',
                  'attributes': ['Negation', u'Confidence'],
                  'type': u'Die',
                  'fgColor': u'black'}],
             'unused': True,
             'bgColor': u'lightgreen',
             'attributes': ['Negation', u'Confidence'],
             'type': u'Life',
             'fgColor': u'black'},
            {'borderColor': u'darken',
             'normalizations': [],
             'name': u'Transaction',
             'labels': None,
             'children': [
                 {'borderColor': u'darken',
                  'normalizations': [],
                  'name': u'Transfer ownership',
                  'arcs': [{'labelArrow': u'none',
                            'arrowHead': u'triangle,5',
                            'color': u'black', 'labels': [u'Buyer'],
                            'dashArray': u',', 'type': u'Buyer-Arg',
                            'targets': [u'Person', u'Organization', u'GPE']},
                           {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                            'color': u'black', 'labels': [u'Seller'],
                            'dashArray': u',', 'type': u'Seller-Arg',
                            'targets': [u'Person', u'Organization', u'GPE']},
                           {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                            'color': u'black', 'labels': [u'Artifact'],
                            'dashArray': u',', 'type': u'Artifact-Arg',
                            'targets': [u'Organization']}],
                  'labels': [u'Transfer ownership'],
                  'children': [],
                  'unused': False,
                  'bgColor': u'lightgreen',
                  'attributes': ['Negation', u'Confidence'],
                  'type': u'Transfer-ownership',
                  'fgColor': u'black'
                  }, {
                     'borderColor': u'darken', 'normalizations': [],
                     'name': u'Transfer money',
                     'arcs': [{'labelArrow': u'none',
                               'arrowHead': u'triangle,5', 'color': u'black',
                               'labels': [u'Giver'], 'dashArray': u',',
                               'type': u'Giver-Arg',
                               'targets': [u'Person', u'Organization', u'GPE']},
                              {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                               'color': u'black', 'labels': [u'Recipient'],
                               'dashArray': u',', 'type': u'Recipient-Arg',
                               'targets': [u'Person', u'Organization', u'GPE']},
                              {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                               'color': u'black', 'labels': [u'Beneficiary'],
                               'dashArray': u',', 'type': u'Beneficiary-Arg',
                               'targets': [u'Person', u'Organization', u'GPE']},
                              {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                               'color': u'black', 'labels': [u'Money'],
                               'dashArray': u',', 'type': u'Money-Arg',
                               'targets': [u'Money']}],
                     'labels': [u'Transfer money'], 'children': [],
                     'unused': False, 'bgColor': u'lightgreen',
                     'attributes': ['Negation', u'Confidence'],
                     'type': u'Transfer-money', 'fgColor': u'black'}],
             'unused': True,
             'bgColor': u'lightgreen',
             'attributes': ['Negation', u'Confidence'],
             'type': u'Transaction',
             'fgColor': u'black'},
            {'borderColor': u'darken',
             'normalizations': [],
             'name': u'Business',
             'labels': None,
             'children': [{'borderColor': u'darken', 'normalizations': [], 'name': u'Start org',
                           'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5',
                                     'color': u'black', 'labels': [u'Agent'], 'dashArray': u',',
                                     'type': u'Agent-Arg', 'targets': [u'Person', u'Organization',
                                                                       u'GPE']},
                                    {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                                     'color': u'black', 'labels': [u'Org'], 'dashArray': u',',
                                     'type': u'Org-Arg', 'targets': [u'Organization']}],
                           'labels': [u'Start org'], 'children': [], 'unused': False,
                           'bgColor': u'lightgreen', 'attributes': ['Negation', u'Confidence'],
                           'type': u'Start-org', 'fgColor': u'black'},
                          {'borderColor': u'darken', 'normalizations': [], 'name': u'Merge org',
                           'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5',
                                     'color': u'black', 'labels': [u'Org'], 'dashArray': u',',
                                     'type': u'Org-Arg', 'targets': [u'Organization']}],
                           'labels': [u'Merge org'], 'children': [], 'unused': False,
                           'bgColor': u'lightgreen', 'attributes': ['Negation', u'Confidence'],
                           'type': u'Merge-org', 'fgColor': u'black'}, {'borderColor': u'darken',
                                                                        'normalizations': [],
                                                                        'name': u'End org',
                                                                        'arcs': [{'labelArrow': u'none',
                                                                                  'arrowHead': u'triangle,5',
                                                                                  'color': u'black',
                                                                                  'labels': [u'Org'],
                                                                                  'dashArray': u',',
                                                                                  'type': u'Org-Arg',
                                                                                  'targets': [
                                                                                      u'Organization']}],
                                                                        'labels': [u'End org'],
                                                                        'children': [],
                                                                        'unused': False,
                                                                        'bgColor': u'lightgreen',
                                                                        'attributes': ['Negation',
                                                                                       u'Confidence'],
                                                                        'type': u'End-org',
                                                                        'fgColor': u'black'}],
             'unused': True, 'bgColor': u'lightgreen', 'attributes': ['Negation', u'Confidence'],
             'type': u'Business', 'fgColor': u'black'},
            {'borderColor': u'darken', 'normalizations': [], 'name': u'Report',
             'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'labels': [u'Reporter'], 'dashArray': u',', 'type': u'Reporter-Arg',
                       'targets': [u'Person', u'Organization', u'GPE']},
                      {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'labels': [u'Event'], 'dashArray': u',', 'type': u'Event-Arg',
                       'targets': [u'Life', u'Be-born', u'Marry', u'Divorce', u'Die',
                                   u'Transaction', u'Transfer-ownership', u'Transfer-money',
                                   u'Business', u'Start-org', u'Merge-org', u'End-org', u'Report']}],
             'labels': None, 'children': [], 'unused': False, 'bgColor': u'lightgreen',
             'attributes': ['Negation', u'Confidence'], 'type': u'Report', 'fgColor': u'black'}]
        cls.full_collection_configuration.ui_names = {
            'entities': u'entities',
            'events': u'events',
            'relations': u'relations',
            'attributes': u'attributes'}
        cls.full_collection_configuration.normalization_config = []
        cls.full_collection_configuration.visual_options = {'arc_bundle': 'none', 'text_direction': 'ltr'}
        cls.full_collection_configuration.messages = []
        cls.full_collection_configuration.event_attribute_types = [
            {
                'unused': False,
                'values': [{'box': u'crossed', 'name': 'Negation'}],
                'labels': None,
                'type': 'Negation',
                'name': 'Negation'},
            {'unused': False,
             'values': [{'dashArray': u',', 'name': u'High',
                         'glyph': u'\u2191'},
                        {'dashArray': u',', 'name': u'Neutral',
                         'glyph': u'\u2194'},
                        {'dashArray': u',', 'name': u'Low',
                         'glyph': u'\u2193'}],
             'labels': None,
             'type': u'Confidence',
             'name': u'Confidence'}]
        cls.full_collection_configuration.annotation_logging = False
        cls.full_collection_configuration.ner_taggers = []
        cls.full_collection_configuration.relation_types = [
            {
                'labelArrow': u'none', 'arrowHead': u'triangle,5', 'name': u'Located',
                'args': [{'role': u'Arg1', 'targets': [u'Person']},
                         {'role': u'Arg2', 'targets': [u'GPE']}], 'color': u'black', 'labels': None,
                'children': [], 'unused': False, 'dashArray': u',', 'attributes': [],
                'type': u'Located',
                'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'triangle,5',
             'name': u'Geographical part',
             'args': [{'role': u'Arg1', 'targets': [u'GPE']},
                      {'role': u'Arg2', 'targets': [u'GPE']}],
             'color': u'black', 'labels': [u'Geographical part', u'Geo part'],
             'children': [], 'unused': False, 'dashArray': u',',
             'attributes': [], 'type': u'Geographical_part', 'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'name': u'Family',
             'args': [{'role': u'Arg1', 'targets': [u'Person']},
                      {'role': u'Arg2', 'targets': [u'Person']}],
             'color': u'black', 'labels': None, 'children': [], 'unused': False,
             'dashArray': u',', 'attributes': [], 'type': u'Family', 'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'name': u'Employment',
             'args': [{'role': u'Arg1', 'targets': [u'Person']},
                      {'role': u'Arg2', 'targets': [u'GPE']}], 'color': u'black',
             'labels': [u'Employment', u'Employ'], 'children': [], 'unused': False,
             'dashArray': u',', 'attributes': [], 'type': u'Employment', 'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'name': u'Ownership',
             'args': [{'role': u'Arg1', 'targets': [u'Person']},
                      {'role': u'Arg2', 'targets': [u'Organization']}], 'color': u'black',
             'labels': None, 'children': [], 'unused': False, 'dashArray': u',',
             'attributes': [], 'type': u'Ownership', 'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'name': u'Origin',
             'args': [{'role': u'Arg1', 'targets': [u'Organization']},
                      {'role': u'Arg2', 'targets': [u'GPE']}], 'color': u'black',
             'labels': None, 'children': [], 'unused': False, 'dashArray': u',',
             'attributes': [], 'type': u'Origin', 'properties': {}},
            {'labelArrow': u'none', 'arrowHead': u'none', 'name': u'Alias',
             'args': [{'role': u'Arg1', 'targets': [u'Person']},
                      {'role': u'Arg2', 'targets': [u'Person']}],
             'color': u'black', 'labels': None, 'children': [], 'unused': False,
             'dashArray': u'3,3', 'attributes': [], 'type': u'Alias',
             'properties': {u'symmetric': True, u'transitive': True}}]
        cls.full_collection_configuration.entity_types = [
            {'borderColor': u'darken',
             'normalizations': [],
             'name': u'Person',
             'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'name': u'Located', 'labels': [u'Located'], 'dashArray': u',', 'type': u'Located',
                       'targets': [u'GPE']},
                      {'labelArrow': u'none', 'arrowHead': u'triangle,5',
                       'color': u'black', 'labels': [u'Family'],
                       'dashArray': u',', 'type': u'Family',
                       'targets': [u'Person']},
                      {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'labels': [u'Employment', u'Employ'], 'dashArray': u',',
                       'type': u'Employment', 'targets': [u'GPE']},
                      {'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'labels': [u'Ownership'], 'dashArray': u',', 'type': u'Ownership',
                       'targets': [u'Organization']},
                      {'labelArrow': u'none', 'arrowHead': u'none', 'color': u'black',
                       'labels': [u'Alias'], 'dashArray': u'3,3', 'type': u'Alias',
                       'targets': [u'Person']}],
             'labels': [u'Person'],
             'children': [],
             'unused': False,
             'bgColor': u'#FF821C',
             'attributes': [u'Individual', u'Mention'],
             'type': u'Person',
             'fgColor': u'black'},
            {'borderColor': u'darken', 'normalizations': [], 'name': u'Organization',
             'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5', 'color': u'black',
                       'labels': [u'Origin'], 'dashArray': u',', 'type': u'Origin',
                       'targets': [u'GPE']}], 'labels': [u'Organization', u'Org'],
             'children': [], 'unused': False, 'bgColor': u'#a7c2ff', 'hotkey': u'O',
             'attributes': [u'Individual', u'Mention'], 'type': u'Organization',
             'fgColor': u'black'},
            {'borderColor': u'darken', 'normalizations': [],
             'name': u'Geo-political entity',
             'arcs': [{'labelArrow': u'none', 'arrowHead': u'triangle,5',
                       'color': u'black', 'labels': [u'Geographical part',
                                                     u'Geo part'],
                       'dashArray': u',', 'type': u'Geographical_part',
                       'targets': [u'GPE']}],
             'labels': [u'Geo-political entity', u'GPE'], 'children': [],
             'unused': False, 'bgColor': u'#FFD412', 'hotkey': u'G',
             'attributes': [u'Individual', u'Mention'], 'type': u'GPE',
             'fgColor': u'black'},
            {'borderColor': u'darken',
             'normalizations': [],
             'name': u'Money', 'labels': None,
             'children': [], 'unused': False,
             'bgColor': u'#007000',
             'hotkey': u'M',
             'attributes': [u'Individual', u'Mention'],
             'type': u'Money', 'fgColor': u'white'}]
        cls.full_collection_configuration.relation_attribute_types = []
        cls.full_collection_configuration.initialize()

        cls.mammut_configuration_1 = CollectionConfiguration()
        cls.mammut_configuration_1.description = None
        cls.mammut_configuration_1.disambiguator_config = []
        cls.mammut_configuration_1.entity_attribute_types = [{'labels': None,
                                                              'name': 'gender',
                                                              'type': 'S-gender',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 'm'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'f'}]},
                                                             {'labels': None,
                                                              'name': 'number',
                                                              'type': 'S-number',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 's'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'p'}]},
                                                             {'labels': None,
                                                              'name': 'finiteness',
                                                              'type': 'S-finiteness',
                                                              'unused': False,
                                                              'values': [{'box': 'crossed', 'name': 'inf'}]},
                                                             {'labels': None,
                                                              'name': 'gender',
                                                              'type': 'V-gender',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 'm'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'f'}]},
                                                             {'labels': None,
                                                              'name': 'number',
                                                              'type': 'V-number',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 's'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'p'}]},
                                                             {'labels': None,
                                                              'name': 'tense',
                                                              'type': 'V-tense',
                                                              'unused': False,
                                                              'values': [
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'pre'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'pas'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'fut'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'cop'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'posp'}]},
                                                             {'labels': None,
                                                              'name': 'person',
                                                              'type': 'V-person',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': '1'},
                                                                         {'dashArray': ',', 'glyph': '↑', 'name': '2'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': '3'}]},
                                                             {'labels': None,
                                                              'name': 'mood',
                                                              'type': 'V-mood',
                                                              'unused': False,
                                                              'values': [
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'ind'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'imp'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'sub'}]},
                                                             {'labels': None,
                                                              'name': 'finite',
                                                              'type': 'V-finite',
                                                              'unused': False,
                                                              'values': [
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'part'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'ger'}]},
                                                             {'labels': None,
                                                              'name': 'finiteness',
                                                              'type': 'V-finiteness',
                                                              'unused': False,
                                                              'values': [{'box': 'crossed', 'name': 'inf'}]},
                                                             {'labels': None,
                                                              'name': 'gender',
                                                              'type': 'A-gender',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 'm'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'f'}]},
                                                             {'labels': None,
                                                              'name': 'number',
                                                              'type': 'A-number',
                                                              'unused': False,
                                                              'values': [{'dashArray': ',', 'glyph': '↑', 'name': 's'},
                                                                         {'dashArray': ',', 'glyph': '↑',
                                                                          'name': 'p'}]},
                                                             {'labels': None,
                                                              'name': 'finite',
                                                              'type': 'A-finite',
                                                              'unused': False,
                                                              'values': [{'box': 'crossed', 'name': 'part'}]},
                                                             {'labels': None,
                                                              'name': 'finite',
                                                              'type': 'ADV-finite',
                                                              'unused': False,
                                                              'values': [{'box': 'crossed', 'name': 'ger'}]},
                                                             {'labels': None,
                                                              'name': 'pronominales',
                                                              'type': 'D-pronominales',
                                                              'unused': False,
                                                              'values': [
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'neg'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'int'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'exc'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'prs'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'art'}]},
                                                             {'labels': None,
                                                              'name': 'pronominales',
                                                              'type': 'P-pronominales',
                                                              'unused': False,
                                                              'values': [
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'neg'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'int'},
                                                                  {'dashArray': ',', 'glyph': '↑', 'name': 'prs'}]}]
        cls.mammut_configuration_1.event_types = [{'arcs': [
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Sustantivo', 'S'],
             'name': 'Sustantivo',
             'targets': ['S'],
             'type': 'S-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Verbo', 'V'],
             'name': 'Verbo',
             'targets': ['V'],
             'type': 'V-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Adjetivo', 'A'],
             'name': 'Adjetivo',
             'targets': ['A'],
             'type': 'A-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Adverbio', 'ADV'],
             'name': 'Adverbio',
             'targets': ['ADV'],
             'type': 'ADV-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Interjeccion', 'I'],
             'name': 'Interjeccion',
             'targets': ['I'],
             'type': 'I-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Preposicion', 'PREP'],
             'name': 'Preposicion',
             'targets': ['PREP'],
             'type': 'PREP-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Determinante', 'D'],
             'name': 'Determinante',
             'targets': ['D'],
             'type': 'D-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Pronombre', 'P'],
             'name': 'Pronombre',
             'targets': ['P'],
             'type': 'P-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Conjuncion', 'C'],
             'name': 'Conjuncion',
             'targets': ['C'],
             'type': 'C-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Auxiliar', 'AUX'],
             'name': 'Auxiliar',
             'targets': ['AUX'],
             'type': 'AUX-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Nexus', 'NEX'],
             'name': 'Nexus',
             'targets': ['NEX'],
             'type': 'NEX-Arg'},
            {'arrowHead': 'triangle,5',
             'color': 'black',
             'count': '*',
             'dashArray': ',',
             'labelArrow': 'none',
             'labels': ['Article', 'ART'],
             'name': 'Article',
             'targets': ['ART'],
             'type': 'ART-Arg'}],
            'attributes': [],
            'bgColor': 'lightgreen',
            'borderColor': 'darken',
            'children': [],
            'fgColor': 'black',
            'keys_by_type': {'A': ['A-Arg'],
                             'ADV': ['ADV-Arg'],
                             'ART': ['ART-Arg'],
                             'AUX': ['AUX-Arg'],
                             'C': ['C-Arg'],
                             'D': ['D-Arg'],
                             'I': ['I-Arg'],
                             'NEX': ['NEX-Arg'],
                             'P': ['P-Arg'],
                             'PREP': ['PREP-Arg'],
                             'S': ['S-Arg'],
                             'V': ['V-Arg']},
            'labels': ['LocV', 'LOC_V'],
            'name': 'LocV',
            'normalizations': [],
            'type': 'LOC_V',
            'unused': False}]
        cls.mammut_configuration_1.ui_names = {'attributes': 'features', 'entities': 'pos', 'events': 'pos-arcs',
                                               'relations': 'relations'}
        cls.mammut_configuration_1.normalization_config = []
        cls.mammut_configuration_1.visual_options = {'arc_bundle': 'none', 'text_direction': 'ltr'}
        cls.mammut_configuration_1.messages = []
        cls.mammut_configuration_1.event_attribute_types = []
        cls.mammut_configuration_1.annotation_logging = False
        cls.mammut_configuration_1.ner_taggers = []
        cls.mammut_configuration_1.relation_types = []
        cls.mammut_configuration_1.entity_types = [{'arcs': [],
                                                    'attributes': ['S-gender', 'S-number', 'S-finiteness'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Sustantivo', 'S'],
                                                    'name': 'Sustantivo',
                                                    'normalizations': [],
                                                    'type': 'S',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': ['V-gender',
                                                                   'V-number',
                                                                   'V-tense',
                                                                   'V-person',
                                                                   'V-mood',
                                                                   'V-finite',
                                                                   'V-finiteness'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Verbo', 'V'],
                                                    'name': 'Verbo',
                                                    'normalizations': [],
                                                    'type': 'V',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': ['A-gender', 'A-number', 'A-finite'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Adjetivo', 'A'],
                                                    'name': 'Adjetivo',
                                                    'normalizations': [],
                                                    'type': 'A',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': ['ADV-finite'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Adverbio', 'ADV'],
                                                    'name': 'Adverbio',
                                                    'normalizations': [],
                                                    'type': 'ADV',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Interjeccion', 'I'],
                                                    'name': 'Interjeccion',
                                                    'normalizations': [],
                                                    'type': 'I',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Preposicion', 'PREP'],
                                                    'name': 'Preposicion',
                                                    'normalizations': [],
                                                    'type': 'PREP',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': ['D-tipos pronominales'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Determinante', 'D'],
                                                    'name': 'Determinante',
                                                    'normalizations': [],
                                                    'type': 'D',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': ['P-tipos pronominales'],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Pronombre', 'P'],
                                                    'name': 'Pronombre',
                                                    'normalizations': [],
                                                    'type': 'P',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Conjuncion', 'C'],
                                                    'name': 'Conjuncion',
                                                    'normalizations': [],
                                                    'type': 'C',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Auxiliar', 'AUX'],
                                                    'name': 'Auxiliar',
                                                    'normalizations': [],
                                                    'type': 'AUX',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Nexus', 'NEX'],
                                                    'name': 'Nexus',
                                                    'normalizations': [],
                                                    'type': 'NEX',
                                                    'unused': False},
                                                   {'arcs': [],
                                                    'attributes': [],
                                                    'bgColor': '#FF821C',
                                                    'borderColor': 'darken',
                                                    'children': [],
                                                    'fgColor': 'black',
                                                    'keys_by_type': {},
                                                    'labels': ['Article', 'ART'],
                                                    'name': 'Article',
                                                    'normalizations': [],
                                                    'type': 'ART',
                                                    'unused': False}]
        cls.mammut_configuration_1.relation_attribute_types = []
        cls.mammut_configuration_1.initialize()

    def setUp(self):
        print("Starting test...")
        text = u"Welcome to the Brat Rapid Annotation Tool (brat) tutorial!\n\nbrat is a web-based tool for structured text annotation and visualization. The easiest way to explain what this means is by example: see the following sentence illustrating various types of annotation. Take a moment to study this example, moving your mouse cursor over some of the annotations. Hold the cursor still over an annotation for more detail.\n\n\n1 ) Citibank was involved in moving about $100 million for Raul Salinas de Gortari, brother of a former Mexican president, to banks in Switzerland.\n\n\nIf this example seems complicated, don't panic! This tutorial will present the key features of brat interactively, with each document presenting one or a few features. If you follow this brief tutorial, you'll be able to understand and create annotations such as those above in no time.\n\nTry moving to the next document now by clicking on the arrow to the right on the blue bar at the top left corner of the page.\n"
        token_offsets = [(0, 7), (8, 10), (11, 14), (15, 19), (20, 25), (26, 36), (37, 41),
                         (42, 48), (49, 58),
                         (60, 64), (65, 67), (68, 69), (70, 79), (80, 84), (85, 88), (89, 99),
                         (100, 104), (105, 115),
                         (116, 119), (120, 134), (135, 138), (139, 146), (147, 150), (151, 153),
                         (154, 161),
                         (162, 166), (167, 171), (172, 177), (178, 180), (181, 183), (184, 192),
                         (193, 196),
                         (197, 200), (201, 210), (211, 219), (220, 232), (233, 240), (241, 246),
                         (247, 249),
                         (250, 261), (262, 266), (267, 268), (269, 275), (276, 278), (279, 284),
                         (285, 289),
                         (290, 298), (299, 305), (306, 310), (311, 316), (317, 323), (324, 328),
                         (329, 333),
                         (334, 336), (337, 340), (341, 353), (354, 358), (359, 362), (363, 369),
                         (370, 375),
                         (376, 380), (381, 383), (384, 394), (395, 398), (399, 403), (404, 411),
                         (414, 415),
                         (416, 417), (418, 426), (427, 430), (431, 439), (440, 442), (443, 449),
                         (450, 455),
                         (456, 460), (461, 468), (469, 472), (473, 477), (478, 485), (486, 488),
                         (489, 497),
                         (498, 505), (506, 508), (509, 510), (511, 517), (518, 525), (526, 536),
                         (537, 539),
                         (540, 545), (546, 548), (549, 561), (564, 566), (567, 571), (572, 579),
                         (580, 585),
                         (586, 598), (599, 604), (605, 611), (612, 616), (617, 625), (626, 630),
                         (631, 638),
                         (639, 642), (643, 646), (647, 655), (656, 658), (659, 663), (664, 678),
                         (679, 683),
                         (684, 688), (689, 697), (698, 708), (709, 712), (713, 715), (716, 717),
                         (718, 721),
                         (722, 731), (732, 734), (735, 738), (739, 745), (746, 750), (751, 756),
                         (757, 766),
                         (767, 773), (774, 776), (777, 781), (782, 784), (785, 795), (796, 799),
                         (800, 806),
                         (807, 818), (819, 823), (824, 826), (827, 832), (833, 838), (839, 841),
                         (842, 844),
                         (845, 850), (852, 855), (856, 862), (863, 865), (866, 869), (870, 874),
                         (875, 883),
                         (884, 887), (888, 890), (891, 899), (900, 902), (903, 906), (907, 912),
                         (913, 915),
                         (916, 919), (920, 925), (926, 928), (929, 932), (933, 937), (938, 941),
                         (942, 944),
                         (945, 948), (949, 952), (953, 957), (958, 964), (965, 967), (968, 971),
                         (972, 977)]
        sentence_offsets = [(0, 58), (60, 411), (414, 561), (564, 850), (852, 977)]
        self.intro_document = Document(text, token_offsets, sentence_offsets, self.full_collection_configuration)
        self.intro_document.ctime = 1498628240.0
        self.intro_document.mtime = 1498628240.0
        self.intro_document.entities = [
            [u'T1', u'Organization', [(418, 426)]],
            [u'T2', u'Money', [(456, 468)]],
            [u'T4', u'Person', [(473, 496)]],
            [u'T5', u'Person', [(511, 535)]],
            [u'T6', u'Organization', [(540, 545)]],
            [u'T7', u'GPE', [(549, 560)]],
            [u'T8', u'Person', [(290, 297)]],
            [u'T9', u'Organization', [(311, 316)]],
            [u'T10', u'Organization', [(299, 305)]],
            [u'T12', u'Person', [(659, 688)]],
            # Triggers
            [u'T3', u'Transfer-money', [(443, 449)]],
            [u'T11', u'End-org', [(329, 333)]],
            [u'T13', u'Divorce', [(722, 730)]]
        ]
        self.intro_document.relations = [[u'R2', u'Origin', [(u'Arg1', u'T6'), (u'Arg2', u'T7')]],
                                         [u'R1', u'Family', [(u'Arg1', u'T4'), (u'Arg2', u'T5')]]]
        self.intro_document.events = [
            [u'E1', u'T3', [(u'Giver-Arg', u'T1'), (u'Money-Arg', u'T2'), (u'Beneficiary-Arg', u'T4'),
                            (u'Recipient-Arg', u'T6')]],
            [u'E2', u'T11', []],
            [u'E3', u'T13', []]]
        self.intro_document.attributes = [[u'A1', u'Mention', u'T4', u'Name'],
                                          [u'A2', u'Individual', u'T4', True],
                                          [u'A3', u'Mention', u'T5', u'Nominal'],
                                          [u'A4', u'Individual', u'T5', True],
                                          [u'A5', u'Confidence', u'E1', u'High'],
                                          [u'A6', u'Mention', u'T8', u'Name'],
                                          [u'A7', u'Individual', u'T8', True],
                                          [u'A8', u'Mention', u'T9', u'Nominal'],
                                          [u'A9', u'Individual', u'T9', True],
                                          [u'A10', u'Confidence', u'E2', u'High']]
        self.intro_document.comments = [[u'T2', u'AnnotatorNotes', u'100000000 USD'],
                                        (u'E2', 'AnnotationIncomplete',
                                         u'Incomplete: exactly one Org argument required for event'),
                                        (u'E3', 'AnnotationIncomplete',
                                         u'Incomplete: exactly 2 Person arguments required for event')]
        self.intro_document.equivs = []
        self.intro_document.normalizations = [[u'N1', u'Reference', u'T5', u'Wikipedia', u'64488',
                                               u'Carlos Salinas de Gortari']]
        self.intro_document.modifications = []
        self.intro_document.initialize()

        mammut_document_text_1 = '¿Van hoy a hacer ofertas especiales en Franca?'
        mammut_document_token_offsets_1 = []
        mammut_document_sentence_offsets_1 = [(0, 45)]
        self.mammut_document_1 = Document(mammut_document_text_1, mammut_document_token_offsets_1,
                                     mammut_document_sentence_offsets_1,
                                     self.mammut_configuration_1)
        self.mammut_document_1.ctime = 1498628240.0
        self.mammut_document_1.mtime = 1498628240.0
        self.mammut_document_1.initialize()

    def test_01_create_span_create_entity_1(self):
        json_data = """{
      "action": "createSpan",
      "offsets": "[[384,394]]",
      "type": "Money",
      "comment": "prueba",
      "attributes": "{\\"Individual\\":true,\\"Mention\\":\\"Nominal\\"}",
      "normalizations": "[]",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        try:
            res = self.intro_document.create_span(data)
            self.intro_document.update_lists()
            for e in self.intro_document.entities:
                if e[1] == 'Money' and e[2][0][0] == 384 and e[2][0][1] == 394:
                    entity_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(entity_found, 'New entity not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_01_create_span_create_entity_2(self):
        json_data = """{
        "action":"createSpan",
        "offsets":"[[1,4]]",
        "type":"AUX",
        "comment":"",
        "attributes":"{\\"S-finiteness\\":false,\\"V-finiteness\\":false,\\"A-finite\\":false,\\"ADV-finite\\":false}",
        "normalizations":"[]",
        "protocol":1}"""
        data = json.loads(json_data)
        entity_found = False
        try:
            res = self.mammut_document_1.create_span(data)
            self.mammut_document_1.update_lists()
            for e in self.mammut_document_1.entities:
                if e[1] == 'AUX' and e[2][0][0] == 1 and e[2][0][1] == 4:
                    entity_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(entity_found, 'New entity not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_02_create_span_create_event_1(self):
        json_data = """{
      "action": "createSpan",
      "offsets": "[[354,358]]",
      "type": "Transfer-money",
      "comment": "prueba",
      "attributes": "{\\"Negation\\":true,\\"Confidence\\":\\"High\\"}",
      "normalizations": "[]",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        try:
            res = self.intro_document.create_span(data)
            self.intro_document.update_lists()
            for e in self.intro_document.entities:
                if e[1] == 'Transfer-money' and e[2][0][0] == 354 and e[2][0][1] == 358:
                    entity_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(entity_found, 'New entity not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_03_create_span_edit_entity_1(self):
        json_data = """{
      "action": "createSpan",
      "offsets": "[[511, 535]]",
      "type": "Person",
      "id": "T5",
      "comment": "prueba2",
      "attributes": "{\\"Individual\\":true,\\"Mention\\":\\"Nominal\\"}",
      "normalizations": "[]",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        comment_found = False
        try:
            res = self.intro_document.create_span(data)
            self.intro_document.update_lists()
            for e in self.intro_document.entities:
                if e[1] == 'Person' and e[2][0][0] == 511 and e[2][0][1] == 535:
                    entity_found = True
                    break
            for c in self.intro_document.comments:
                if c[0] == 'T5' and c[1] == 'AnnotatorNotes' and c[2] == '\tprueba2':
                    comment_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(entity_found, 'Edited entity not found')
        self.assertTrue(comment_found, 'New comment not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_04_create_span_edit_event_1(self):
        json_data = """{
      "action": "createSpan",
      "offsets": "[[329, 333]]",
      "type": "End-org",
      "id": "E2",
      "comment": "prueba2",
      "attributes": "{\\"Confidence\\":\\"High\\"}",
      "normalizations": "[]",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        comment_found = False
        try:
            res = self.intro_document.create_span(data)
            self.intro_document.update_lists()
            for e in self.intro_document.entities:
                if e[1] == 'End-org' and e[2][0][0] == 329 and e[2][0][1] == 333:
                    entity_found = True
                    break
            for c in self.intro_document.comments:
                if c[0] == 'E2' and c[1] == 'AnnotatorNotes' and c[2] == '\tprueba2':
                    comment_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(entity_found, 'Edited event not found')
        self.assertTrue(comment_found, 'New comment not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_05_delete_span_delete_entity_1(self):
        json_data = """{
      "action": "deleteSpan",
      "offsets": "[[659, 688]]",
      "type": "Person",
      "id": "T12",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        try:
            for e in self.intro_document.entities:
                if e[0] == 'T12':
                    entity_found = True
                    break
            self.assertTrue(entity_found, 'Initial entity not found')
            res = self.intro_document.delete_span(data['id'])
            self.intro_document.update_lists()
            entity_found = False
            for e in self.intro_document.entities:
                if e[0] == 'T12':
                    entity_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertFalse(entity_found, 'Deleted entity was found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_06_delete_span_delete_event_1(self):
        json_data = """{
      "action": "deleteSpan",
      "offsets": "[[722, 730]]",
      "type": "Divorce",
      "id": "E3",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        entity_found = False
        event_found = False
        try:
            for e in self.intro_document.events:
                if e[0] == 'E3':
                    event_found = True
                    break
            self.assertTrue(event_found, 'Initial entity not found')
            for e in self.intro_document.entities:
                if e[0] == 'T13':
                    entity_found = True
                    break
            self.assertTrue(entity_found, 'Initial entity not found')
            res = self.intro_document.delete_span(data['id'])
            self.intro_document.update_lists()
            event_found = False
            for e in self.intro_document.events:
                if e[0] == 'E3':
                    event_found = True
                    break
            entity_found = False
            for e in self.intro_document.entities:
                if e[0] == 'T13':
                    entity_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertFalse(entity_found, 'Deleted entity was found')
        self.assertFalse(event_found, 'Deleted event was found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_11_create_arc_create_arc_1(self):
        json_data = """{
      "action": "createArc",
      "origin": "T8",
      "target": "T7",
      "type": "Located",
      "comment": "Prueba",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        relation_found = False
        try:
            res = self.intro_document.create_arc(data)
            self.intro_document.update_lists()
            for r in self.intro_document.relations:
                if r[1] == 'Located' and r[2][0][1] == "T8" and r[2][1][1] == "T7":
                    relation_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(relation_found, 'New entity not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_12_create_arc_edit_arc_1(self):
        json_data = """{
      "action": "createArc",
      "origin": "T4",
      "target": "T5",
      "old_target": "T5",
      "type": "Alias",
      "old_type": "Family",
      "id": "T4~Family~T5",
      "comment": "Prueba2",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        relation_found = False
        comment_found = False
        try:
            res = self.intro_document.create_arc(data)
            self.intro_document.update_lists()
            relation_id = ''
            for r in self.intro_document.relations:
                if r[1] == 'Alias' and r[2][0][1] == "T4" and r[2][1][1] == "T5":
                    relation_found = True
                    relation_id = r[0]
                    break
            for c in self.intro_document.comments:
                if c[0] == relation_id and c[1] == 'AnnotatorNotes' and c[2] == '\tPrueba2':
                    comment_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertTrue(relation_found, 'Edited relation not found')
        self.assertTrue(comment_found, 'New comment not found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_13_delete_arc_delete_arc_1(self):
        json_data = """{
      "action": "deleteArc",
      "origin": "T4",
      "target": "T5",
      "old_target": "T5",
      "type": "Family",
      "old_type": "Family",
      "id": "T4~Family~T5",
      "protocol": 1
    }"""
        data = json.loads(json_data)
        relation_found = False
        try:
            for r in self.intro_document.relations:
                if r[0] == 'R1':
                    relation_found = True
                    break
            self.assertTrue(relation_found, 'Initial relation not found')
            res = self.intro_document.delete_arc(data['origin'], data['target'], data['type'])
            self.intro_document.update_lists()
            relation_found = False
            for e in self.intro_document.relations:
                if e[0] == 'R1':
                    relation_found = True
                    break
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
        self.assertFalse(relation_found, 'Deleted relation was found')
        msg_count = Messager.get_pending_messages_count()
        self.assertEquals(msg_count, 0, "Some unexpected messages generated.")

    def test_21_instantiate_widget_visualizer_just_entities(self):
        not_error = True
        try:
            just_entities_text = u"Ed O'Kelley was the man who shot the man who shot Jesse James."
            just_entities_token_offsets = []
            just_entities_sentence_offsets = []
            just_entities_document = Document(just_entities_text, just_entities_token_offsets,
                                              just_entities_sentence_offsets,
                                              self.just_entities_collection_configuration)
            just_entities_document.entities = [
                # Format: [${ID}, ${TYPE}, [[${START}, ${END}]]]
                # note that range of the offsets are [${START},${END})
                ['T1', 'Person', [(0, 11)]],
                ['T2', 'Person', [(20, 23)]],
                ['T3', 'Person', [(37, 40)]],
                ['T4', 'Person', [(50, 61)]]
            ]
            just_entities_document.initialize()
            just_entities = Visualizer(value=just_entities_document,
                                       collection_configuration=self.just_entities_collection_configuration)
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
            not_error = False
        self.assertTrue(not_error, '')

    def test_22_instantiate_widget_visualizer_entities_relations_and_events(self):
        not_error = True
        try:
            entities_relations_and_events_text = u"Ed O'Kelley was the man who shot the man who shot Jesse James."
            entities_relations_and_events_token_offsets = []
            entities_relations_and_events_sentence_offsets = []
            entities_relations_and_events_document = Document(entities_relations_and_events_text,
                                                              entities_relations_and_events_token_offsets,
                                                              entities_relations_and_events_sentence_offsets,
                                                              self.entities_relations_and_events_collection_configuration)
            entities_relations_and_events_document.entities = [
                # Format: [${ID}, ${TYPE}, [[${START}, ${END}]]]
                # note that range of the offsets are [${START},${END})
                ['T1', 'Person', [(0, 11)]],
                ['T2', 'Person', [(20, 23)]],
                ['T3', 'Person', [(37, 40)]],
                ['T4', 'Person', [(50, 61)]],
                ["T5", "Assassination", [(45, 49)]],
                ["T6", "Assassination", [(28, 32)]]
            ]
            entities_relations_and_events_document.attributes = [["A1", "Notorious", "T4", True]]
            entities_relations_and_events_document.relations = [
                [
                    "R1",
                    "Anaphora",
                    [["Anaphor", "T2"], ["Entity", "T1"]]
                ]
            ]
            entities_relations_and_events_document.events = [
                [
                    "E1",
                    "T5",
                    [["Perpetrator", "T3"], ["Victim", "T4"]]
                ],
                [
                    "E2",
                    "T6",
                    [["Perpetrator", "T2"], ["Victim", "T3"]]
                ]
            ]
            entities_relations_and_events_document.initialize()
            entities_relations_and_events = Visualizer(value=entities_relations_and_events_document,
                                                       collection_configuration=self.entities_relations_and_events_collection_configuration)
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
            not_error = False
        self.assertTrue(not_error, '')

    def test_23_instantiate_widget_anotator_intro(self):
        not_error = True
        try:
            intro = Annotator(value=self.intro_document,
                              collection_configuration=self.full_collection_configuration,
                              general_configuration=GeneralConfiguration())
        except Exception as ex:
            self.assertTrue(False, 'Error: Unexpected exception: {ex}')
            not_error = False
        self.assertTrue(not_error, '')
