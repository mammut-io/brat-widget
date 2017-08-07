# coding=utf-8
import re

import sys

from brat_widget.messager import Messager
from brat_widget.common import JsonDumpable

ENTITY_CATEGORY, EVENT_CATEGORY, RELATION_CATEGORY, UNKNOWN_CATEGORY = range(4)

# special relation types for marking which spans can overlap
# ENTITY_NESTING_TYPE used up to version 1.3, now deprecated
ENTITY_NESTING_TYPE = "ENTITY-NESTING"
# TEXTBOUND_OVERLAP_TYPE used from version 1.3 onward
TEXTBOUND_OVERLAP_TYPE = "<OVERLAP>"
SPECIAL_RELATION_TYPES = set([ENTITY_NESTING_TYPE,
                              TEXTBOUND_OVERLAP_TYPE])
OVERLAP_TYPE_ARG = '<OVL-TYPE>'

# Reserved strings with special meanings in configuration.
reserved_config_name   = ["ANY", "ENTITY", "RELATION", "EVENT", "NONE", "EMPTY", "REL-TYPE", "URL", "URLBASE", "GLYPH-POS", "DEFAULT", "NORM", "OVERLAP", "OVL-TYPE", "INHERIT"]
# TODO: "GLYPH-POS" is no longer used, warn if encountered and
# recommend to use "position" instead.
reserved_config_string = ["<%s>" % n for n in reserved_config_name]

class InvalidProjectConfigException(Exception):
    pass


class GeneralVisualConfiguration(JsonDumpable):
    def __init__(self):
        self.marginX = 2
        self.marginY = 1
        self.arcTextMargin = 1
        self.boxSpacing = 1
        self.curlyHeight = 4
        self.arcSpacing = 9 # 10
        self.arcStartHeight = 19 # 23 # 25

    def get_dict(self):
        dict = JsonDumpable.get_dict(self)
        dict.update({
            'margin': {
                'x': self.marginX,
                'y': self.marginY
            },
            'arcTextMargin': self.arcTextMargin,
            'boxSpacing': self.boxSpacing,
            'curlyHeight': self.curlyHeight,
            'arcSpacing': self.arcSpacing,
            'arcStartHeight': self.arcStartHeight
        })
        return dict

    def set_from_dict(self, dict):
        JsonDumpable.set_from_dict(self, dict)
        self.marginX = dict['margin']['x']
        self.marginY = dict['margin']['y']
        self.arcTextMargin = dict['arcTextMargin']
        self.boxSpacing = dict['boxSpacing']
        self.curlyHeight = dict['curlyHeight']
        self.arcSpacing = dict['arcSpacing']
        self.arcStartHeight = dict['arcStartHeight']


class GeneralConfiguration(JsonDumpable):
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
        dict = JsonDumpable.get_dict(self)
        dict.update({
            'abbrevsOn': self.abbrevsOn,
            'textBackgrounds': self.textBackgrounds,
            'svgWidth': self.svgWidth,
            'rapidModeOn': self.rapidModeOn,
            'confirmModeOn': self.confirmModeOn,
            'autorefreshOn': self.autorefreshOn,
            'typeCollapseLimit': self.typeCollapseLimit,
            'visual': self.visual.get_dict()
        })
        return dict

    def set_from_dict(self, dict):
        JsonDumpable.set_from_dict(self, dict)
        self.abbrevsOn = dict['abbrevsOn']
        self.textBackgrounds = dict['textBackgrounds']
        self.svgWidth = dict['svgWidth']
        self.rapidModeOn = dict['rapidModeOn']
        self.confirmModeOn = dict['confirmModeOn']
        self.autorefreshOn = dict['autorefreshOn']
        self.typeCollapseLimit = dict['typeCollapseLimit']
        self.visual.set_from_dict(dict['visual'])


def collect_type_list(node, collected):
    collected.append(node)
    if 'children' in node:
        for c in node['children']:
            collect_type_list(c, collected)
    return collected

def type_hierarchy_to_list(hierarchy):
    root_nodes = hierarchy
    types = []
    for n in root_nodes:
        collect_type_list(n, types)
    return types

# fallback for missing or partial config: these are highly likely to
# be entity (as opposed to an event or relation) types.
# TODO: remove this workaround once the configs stabilize.
# This hack is inherited from brat
very_likely_physical_entity_types = [
    # 'Protein',
    # 'Entity',
    # 'Organism',
    # 'Chemical',
    # 'Two-component-system',
    # 'Regulon-operon',
    # # for more PTM annotation
    # 'Protein_family_or_group',
    # 'DNA_domain_or_region',
    # 'Protein_domain_or_region',
    # 'Amino_acid_monomer',
    # 'Carbohydrate',
    # # for AZ corpus
    # 'Cell_type',
    # 'Drug_or_compound',
    # 'Gene_or_gene_product',
    # 'Tissue',
    # #'Not_sure',
    # #'Other',
    # 'Other_pharmaceutical_agent',
    ]

class CollectionConfiguration(JsonDumpable):
    def __init__(self):
        self.description = None
        self.disambiguator_config = []
        self.entity_types = []
        self.entity_attribute_types = []
        self.event_types = []
        self.event_attribute_types = []
        self.relation_types = []
        self.relation_attribute_types = []
        self.ui_names = {'entities': u'entities',
                     'events': u'events',
                     'relations': u'relations',
                     'attributes': u'attributes'}
        self.normalization_config = []
        self.visual_options = {}
        self.messages = []
        self.annotation_logging = False
        self.ner_taggers = []
        # computed and private fields
        self._planed_entity_types = []
        self._planed_entity_attribute_types = []
        self._planed_event_types = []
        self._planed_event_attribute_types = []
        self._planed_relation_types = []
        self._planed_relation_attribute_types = []
        self._dict_entity_types = {}
        self._dict_entity_attribute_types = {}
        self._dict_event_types = {}
        self._dict_event_attribute_types = {}
        self._dict_relation_types = {}
        self._dict_relation_attribute_types = {}
        self._labels_by_storage_form = {}

    def initialize(self):
        def handle_arguments(a, keys_by_type, special_arguments):
            if 'targets' in a:
                # if a['type'] in reserved_config_string:
                #     if a['type'] is special_arguments:
                #         Messager.warning(
                #             "Project configuration: error parsing: %s argument '%s' appears multiple times." % (
                #                 a['type'],
                #                 5))
                #         raise InvalidProjectConfigException()
                #     special_arguments[a['type']] = a['targets']
                #     # NOTE: skip the rest of processing -- don't add in normal args
                # else:
                    for t in a['targets']:
                        if t not in keys_by_type:
                            keys_by_type[t] = []
                        keys_by_type[t].append(a['type'])

        def add_label_by_storage_form(dict):
            if 'name' in dict:
                self._labels_by_storage_form[dict['type']] = dict['name']
            else:
                self._labels_by_storage_form[dict['type']] = dict['type']

        def populate_dict(src_hierarchy, dst_planed_list, dst_dict):
            for t in type_hierarchy_to_list(src_hierarchy):
                dst_planed_list.append(t)
                dst_dict[t['type']] = t
                add_label_by_storage_form(t)

        populate_dict(self.entity_types, self._planed_entity_types, self._dict_entity_types)
        populate_dict(self.entity_attribute_types, self._planed_entity_attribute_types, self._dict_entity_attribute_types)
        populate_dict(self.event_types, self._planed_event_types, self._dict_event_types)
        populate_dict(self.event_attribute_types, self._planed_event_attribute_types, self._dict_event_attribute_types)
        populate_dict(self.relation_types, self._planed_relation_types, self._dict_relation_types)
        populate_dict(self.relation_attribute_types, self._planed_relation_attribute_types, self._dict_relation_attribute_types)
        for e in self._planed_event_types:
            keys_by_type = {}
            # special case (sorry): if the key is a reserved config
            # string (e.g. "<REL-TYPE>" or "<URL>"), parse differently
            # and store separately
            special_arguments = {}
            if 'arcs' in e:
                for a in e['arcs']:
                    add_label_by_storage_form(a)
                    handle_arguments(a, keys_by_type, special_arguments)
            e['keys_by_type'] = keys_by_type
            # e['special_arguments'] = special_arguments
        for e in self._planed_entity_types:
            keys_by_type = {}
            special_arguments = {}
            if 'arcs' in e:
                for a in e['arcs']:
                    add_label_by_storage_form(a)
                    handle_arguments(a, keys_by_type, special_arguments)
            e['keys_by_type'] = keys_by_type
            # e['special_arguments'] = special_arguments

    def get_dict(self):
        dict = JsonDumpable.get_dict(self)
        dict.update({
            'description': self.description,
            'disambiguator_config': self.disambiguator_config,
            'entity_attribute_types': self.entity_attribute_types,
            'event_types': self.event_types,
            'ui_names': self.ui_names,
            'normalization_config': self.normalization_config,
            'visual_options': self.visual_options,
            'messages': self.messages,
            'event_attribute_types': self.event_attribute_types,
            'annotation_logging': self.annotation_logging,
            'ner_taggers': self.ner_taggers,
            'relation_types': self.relation_types,
            'entity_types': self.entity_types,
            'relation_attribute_types': self.relation_attribute_types
        })
        return dict

    def set_from_dict(self, dict):
        JsonDumpable.set_from_dict(self, dict)
        self.description = dict['description']
        self.disambiguator_config = dict['disambiguator_config']
        self.entity_attribute_types = dict['entity_attribute_types']
        self.event_types = dict['event_types']
        self.ui_names = dict['ui_names']
        self.normalization_config = dict['normalization_config']
        self.visual_options = dict['visual_options']
        self.messages = dict['messages']
        self.event_attribute_types = dict['event_attribute_types']
        self.annotation_logging = dict['annotation_logging']
        self.ner_taggers = dict['ner_taggers']
        self.relation_types = dict['relation_types']
        self.entity_types = dict['entity_types']
        self.relation_attribute_types = dict['relation_attribute_types']

    def is_event_type(self, t):
        return t in self.get_event_types()

    def get_event_type_list(self):
        return self._planed_event_types

    def get_event_types(self):
        return [t['type'] for t in self._planed_event_types]

    #This implementation is inherited from brat
    def is_physical_entity_type(self, t):
        if t in self.get_entity_types() or t in self.get_event_types():
            return t in self.get_entity_types()
        # TODO: remove this temporary hack
        if t in very_likely_physical_entity_types:
            return True
        return t in self.get_entity_types()

    def get_entity_type_list(self):
        return self._planed_entity_types

    def get_entity_types(self):
        return [t['type'] for t in self._planed_entity_types]

    def is_relation_type(self, t):
        return t in self.get_relation_types()

    def get_relation_type_list(self):
        return self._planed_relation_types

    def get_relation_types(self):
        return [t['type'] for t in self._planed_relation_types]

    def type_category(self, t):
        """
        Returns the category of the given type t.
        The categories can be compared for equivalence but offer
        no other interface.
        """
        if self.is_physical_entity_type(t):
            return ENTITY_CATEGORY
        elif self.is_event_type(t):
            return EVENT_CATEGORY
        elif self.is_relation_type(t):
            return RELATION_CATEGORY
        else:
            # TODO: others
            return UNKNOWN_CATEGORY

    def preferred_display_form(self, t):
        """
        Given a storage form label, returns the preferred display form
        as defined by the label configuration (labels.conf)
        """
        return self._labels_by_storage_form[t]

    def attributes_for(self, ann_type):
        """
        Returs a list of the possible attribute types for an
        annotation of the given type.
        """
        attrs = []
        if self.is_event_type(ann_type):
            if 'attributes' in self._dict_event_types[ann_type]:
                attrs = self._dict_event_types[ann_type]['attributes']
        elif self.is_physical_entity_type(ann_type):
            if 'attributes' in self._dict_entity_types[ann_type]:
                attrs = self._dict_entity_types[ann_type]['attributes']
        elif self.is_relation_type(ann_type):
            if 'attributes' in self._dict_relation_types[ann_type]:
                attrs = self._dict_relation_types[ann_type]['attributes']
        return attrs

    def argument_minimum_count_for_event(self, atype, arg):
        return self._argument_count_for_event(atype, arg, False)

    def argument_maximum_count_for_event(self, atype, arg):
        return self._argument_count_for_event(atype, arg, True)

    def _argument_count_for_event(self, atype, arg, out_max):
        count = 0
        if atype in self._dict_event_types:
            et = self._dict_event_types[atype]
            if 'arcs' in et:
                for arc in et['arcs']:
                    if arg == arc['type']:
                        count_str = ''
                        if 'count' in arc:
                            count_str = arc['count']
                        count = self._get_count_from_str(count_str, out_max)
            if count == 0:
                Messager.warning("Project configuration: unknown argument %s for event type %s. Configuration may be wrong." % (arg, atype))
        else:
            Messager.warning("Project configuration: unknown event type %s. Configuration may be wrong." % atype)
        return count

    def _get_count_from_str(self, count_str, out_max):
        if count_str == '':
            # exactly one
            minimum_count = 1
            maximum_count = 1
        elif count_str == '?':
            # zero or one
            minimum_count = 0
            maximum_count = 1
        elif count_str == '*':
            # any number
            minimum_count = 0
            maximum_count = sys.maxint
        elif count_str == '+':
            # one or more
            minimum_count = 1
            maximum_count = sys.maxint
        else:
            # exact number or range constraint
            assert '{' in count_str and '}' in count_str, "INTERNAL ERROR"
            m = re.match(r'\{(\d+)(?:-(\d+))?\}$', count_str)
            if not m:
                Messager.warning(
                    "Project configuration: error parsing range '%s' (syntax is '{MIN-MAX}')." % (
                        count_str), 5)
                raise InvalidProjectConfigException()
            n1, n2 = m.groups()
            n1 = int(n1)
            if n2 is None:
                # exact number
                if n1 == 0:
                    Messager.warning(
                        "Project configuration: cannot have exactly 0 repetitions of argument '%s'." % (count_str), 5)
                    raise InvalidProjectConfigException()
                minimum_count = n1
                maximum_count = n1
            else:
                # range
                n2 = int(n2)
                if n1 > n2:
                    Messager.warning(
                        "Project configuration: invalid range %d-%d for argument '%s'." % (n1, n2, count_str), 5)
                    raise InvalidProjectConfigException()
                minimum_count = n1
                maximum_count = n2
        if out_max:
            return maximum_count
        else:
            return minimum_count

    def arc_types_from(self, from_ann):
        return self.arc_types_from_to(from_ann)

    def arc_types_from_to(self, from_ann, to_ann="<ANY>", include_special=False):
        """
        Returns the possible arc types that can connect an annotation
        of type from_ann to an annotation of type to_ann.
        If to_ann has the value \"<ANY>\", returns all possible arc types.
        """

        from_node = self.get_node_by_storage_form(from_ann)

        if from_node is None:
            Messager.warning("Project configuration: unknown textbound/event type %s. Configuration may be wrong." % from_ann)
            return []

        if to_ann == "<ANY>":
            relations_from = self.get_relations_by_arg1(from_ann, include_special)
            # TODO: consider using from_node.arg_list instead of .arguments for order
            from_node_arguments = []
            if 'arcs' in from_node:
                for arc in from_node['arcs']:
                    from_node_arguments.append(arc['type'])
            return self.unique_preserve_order(from_node_arguments + [r['type'] for r in relations_from])

        # specific hits
        types = from_node['keys_by_type'].get(to_ann, [])

        if "<ANY>" in from_node['keys_by_type']:
            types += from_node['keys_by_type']["<ANY>"]

        # generic arguments
        if self.is_event_type(to_ann) and '<EVENT>' in from_node['keys_by_type']:
            types += from_node['keys_by_type']['<EVENT>']
        if self.is_physical_entity_type(to_ann) and '<ENTITY>' in from_node['keys_by_type']:
            types += from_node['keys_by_type']['<ENTITY>']

        # relations
        types.extend(self.relation_types_from_to(from_ann, to_ann))

        return self.unique_preserve_order(types)

    def get_node_by_storage_form(self, term):
        if term in self._dict_entity_types:
            if term in self._dict_event_types:
                Messager.warning(
                    "Project configuration: term %s appears multiple times, only using last. Configuration may be wrong." % term,
                    5)
            return self._dict_entity_types[term]
        elif term in self._dict_event_types:
            return self._dict_event_types[term]
        else:
            return None

    def __directory_relations_by_arg_num(self, num, atype, include_special=False):
        assert num >= 0 and num < 2, "INTERNAL ERROR"

        rels = []

        entity_types = self._planed_entity_types
        event_types = self._planed_event_types

        for r in self.get_relation_type_list():
            # "Special" nesting relations ignored unless specifically
            # requested
            if r['type'] in SPECIAL_RELATION_TYPES and not include_special:
                continue

            if len(r['args']) != 2:
                # Don't complain about argument constraints for unused relations
                if not r.unused:
                    Messager.warning("Relation type %s has %d arguments in configuration (%s; expected 2). Please fix configuration." % (r['type'], len(r['args']), ",".join(r['args'])))
            else:
                types = r['args'][num]['targets']
                for type_ in types:
                    # TODO: there has to be a better way
                    if (type_ == atype or
                        type_ == "<ANY>" or
                        atype == "<ANY>" or
                        (type_ in entity_types and atype == "<ENTITY>") or
                        (type_ in event_types and atype == "<EVENT>") or
                        (atype in entity_types and type_ == "<ENTITY>") or
                        (atype in event_types and type_ == "<EVENT>")):
                        rels.append(r)
                        # TODO: why not break here?

        return rels

    def get_relations_by_arg1(self, atype, include_special=False):
        return self.__directory_relations_by_arg_num(0, atype, include_special)

    def get_relations_by_arg2(self, atype, include_special=False):
        return self.__directory_relations_by_arg_num(1, atype, include_special)

    # helper; doesn't really belong here
    # TODO: shouldn't we have an utils.py or something for stuff like this?
    def unique_preserve_order(self, iterable):
        seen = set()
        uniqued = []
        for i in iterable:
            if i not in seen:
                seen.add(i)
                uniqued.append(i)
        return uniqued

    def relation_types_from_to(self, from_ann, to_ann, include_special=False):
        """
        Returns the possible relation types that can have the
        given arg1 and arg2.
        """
        types = []

        t1r = self.get_relations_by_arg1(from_ann, include_special)
        t2r = self.get_relations_by_arg2(to_ann, include_special)

        for r in t1r:
            if r in t2r:
                types.append(r['type'])

        return types

    def mandatory_arguments_for_event(self, atype):
        """
        Returns the mandatory argument types that must be present for
        an annotation of the given type.
        """
        if atype in self._dict_event_types:
            et = self._dict_event_types[atype]
            res = []
            if 'arcs' in et:
                for arc in et['arcs']:
                    minimum_count = 1
                    if 'count' in arc:
                        count_str = arc['count']
                        minimum_count = self._get_count_from_str(count_str, False)
                    if minimum_count > 0:
                        res.append(arc['type'])
            return res
        else:
            Messager.warning("Project configuration: unknown event type %s. Configuration may be wrong." % atype)
            return []

    def get_relations_by_type(self, _type):
        return self.get_relations_by_storage_form(_type)

    def get_relations_by_storage_form(self, rtype, include_special=False):
        out = {}
        for r in self.get_relation_type_list():
            if (r['type'] in SPECIAL_RELATION_TYPES and
                not include_special):
                continue
            if 'unused' in r and r['unused']:
                continue
            if r['type'] not in out:
                out[r['type']] = []
            out[r['type']].append(r)
        return out.get(rtype, [])

    def span_can_contain(self, inner, outer):
        """
        Returns True if the configuration allows the span of an
        annotation of type inner to (properly) contain an annotation
        of type outer, False otherwise.
        """
        ovl_types = self.overlap_types(inner, outer)
        if 'contain' in ovl_types or '<ANY>' in ovl_types:
            return True
        ovl_types = self.overlap_types(outer, inner)
        if '<ANY>' in ovl_types:
            return True
        return False

    def spans_can_be_equal(self, t1, t2):
        """
        Returns True if the configuration allows the spans of
        annotations of type t1 and t2 to be equal, False otherwise.
        """
        ovl_types = self.overlap_types(t1, t2)
        if 'equal' in ovl_types or '<ANY>' in ovl_types:
            return True
        ovl_types = self.overlap_types(t2, t1)
        if 'equal' in ovl_types or '<ANY>' in ovl_types:
            return True
        return False

    def spans_can_cross(self, t1, t2):
        """
        Returns True if the configuration allows the spans of
        annotations of type t1 and t2 to cross, False otherwise.
        """
        ovl_types = self.overlap_types(t1, t2)
        if 'cross' in ovl_types or '<ANY>' in ovl_types:
            return True
        ovl_types = self.overlap_types(t2, t1)
        if 'cross' in ovl_types or '<ANY>' in ovl_types:
            return True
        return False

    def overlap_types(self, inner, outer):
        """
        Returns the set of annotation overlap types that have been
        configured for the given pair of annotations.
        """
        # TODO: this is O(NM) for relation counts N and M and goes
        # past much of the implemented caching. Might become a
        # bottleneck for annotations with large type systems.
        t1r = self.get_relations_by_arg1(inner, True)
        t2r = self.get_relations_by_arg2(outer, True)

        types = []
        for r in (s for s in t1r if s['type'] in SPECIAL_RELATION_TYPES):
            if r in t2r:
                types.append(r)

        # new-style overlap configuration ("<OVERLAP>") takes precedence
        # over old-style configuration ("ENTITY-NESTING").
        ovl_types = set()

        ovl = [r for r in types if r['type'] == TEXTBOUND_OVERLAP_TYPE]
        nst = [r for r in types if r['type'] == ENTITY_NESTING_TYPE]

        if ovl:
            if nst:
                Messager.warning('Warning: both '+TEXTBOUND_OVERLAP_TYPE+
                                 ' and '+ENTITY_NESTING_TYPE+' defined for '+
                                 '('+inner+','+outer+') in config. '+
                                 'Ignoring latter.')
            for r in ovl:
                if OVERLAP_TYPE_ARG not in r['properties']:
                    Messager.warning('Warning: missing '+OVERLAP_TYPE_ARG+
                                     ' for '+TEXTBOUND_OVERLAP_TYPE+
                                     ', ignoring specification.')
                    continue
                for val in r['properties'][OVERLAP_TYPE_ARG]:
                    ovl_types |= set(val.split('|'))
        elif nst:
            # translate into new-style configuration
            ovl_types = {['contain']}
        else:
            ovl_types = set()

        undefined_types = [t for t in ovl_types if
                           t not in ('contain', 'equal', 'cross', '<ANY>')]
        if undefined_types:
            Messager.warning('Undefined '+OVERLAP_TYPE_ARG+' value(s) '+
                             str(undefined_types)+' for '+
                             '('+inner+','+outer+') in config. ')
        return ovl_types

    def is_equiv_type(self, t):
        return t in self.get_equiv_types()

    def get_equiv_types(self):
        # equivalence relations are those relations that are symmetric
        # and transitive, i.e. that have "symmetric" and "transitive"
        # in their "<REL-TYPE>" special argument values.
        return [t['type'] for t in self.get_relation_type_list()
                if "<REL-TYPE>" in t['properties'] and
                "symmetric" in t['properties']["<REL-TYPE>"] and
                "transitive" in t['properties']["<REL-TYPE>"]]
