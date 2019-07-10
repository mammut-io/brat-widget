# coding=utf-8
import json

from brat_widget.configuration import ENTITY_CATEGORY, EVENT_CATEGORY, RELATION_CATEGORY, UNKNOWN_CATEGORY, CollectionConfiguration
from brat_widget.verify_annotations import verify_annotation

try:
    from config import DEBUG
except ImportError:
    DEBUG = False

from brat_widget.annotation import TextAnnotations, DISCONT_SEP, TextBoundAnnotationWithText, EventAnnotation, TextBoundAnnotation, \
    AttributeAnnotation, NormalizationAnnotation, OnelineCommentAnnotation, ALLOW_RELATIONS_REFERENCE_EVENT_TRIGGERS, \
    DependingAnnotationDeleteError, EquivAnnotation, BinaryRelationAnnotation
from brat_widget.messager import Messager
from brat_widget.common import ProtocolError, JsonDumpable, ProtocolArgumentError


class Document(JsonDumpable):
    def __init__(self, text='', token_offsets=[], sentence_offsets=[],
                 collection_configuration=CollectionConfiguration()):
        self.collection_configuration = collection_configuration
        self.text = text
        self.token_offsets = token_offsets
        self.sentence_offsets = sentence_offsets
        self.ann_obj = None
        self.ctime = 1498628240.0
        self.mtime = 1498628240.0
        self.entities = []
        self.relations = []
        self.events = []
        self.attributes = []
        self.comments = []
        self.equivs = []
        self.normalizations = []
        self.modifications = []

    def initialize(self):
        self.ann_obj = TextAnnotations(self)

    def update_lists(self):
        self.entities = []
        for tb_ann in self.ann_obj.get_textbounds():
            self.entities.append(tb_ann.to_list())
        self.relations = []
        for rel_ann in self.ann_obj.get_relations():
            self.relations.append(rel_ann.to_list())
        self.events = []
        for event_ann in self.ann_obj.get_events():
            self.events.append(event_ann.to_list())
        self.attributes = []
        for att_ann in self.ann_obj.get_attributes():
            self.attributes.append(att_ann.to_list())
        self.comments = []
        for com_ann in self.ann_obj.get_oneline_comments():
            self.comments.append(com_ann.to_list())
        self.equivs = []
        for eq_ann in self.ann_obj.get_equivs():
            self.equivs.append(eq_ann.to_list())
        self.normalizations = []
        for norm_ann in self.ann_obj.get_normalizations():
            self.normalizations.append(norm_ann.to_list())

    def get_dict(self):
        return self._json_from_ann()

    def set_from_dict(self, dict):
        JsonDumpable.set_from_dict(self, dict)
        self.modifications = dict['modifications']
        self.normalizations = dict['normalizations']
        self.ctime = dict['ctime']
        self.text = dict['text']
        self.mtime = dict['mtime']
        self.sentence_offsets = dict['sentence_offsets']
        self.relations = dict['relations']
        self.entities = dict['entities']
        self.comments = dict['comments']
        self.token_offsets = dict['token_offsets']
        self.attributes = dict['attributes']
        self.equivs = dict['equivs']
        self.events = dict['events']
        self.initialize()

    def create_span(self, data):
        # offsets should be JSON string corresponding to a list of (start,
        # end) pairs; convert once at this interface
        offsets = json.loads(data['offsets'])
        type = data['type']
        attributes = None
        if 'attributes' in data:
            attributes = data['attributes']
        normalizations = None
        if 'normalizations' in data:
            normalizations = data['normalizations']
        id = None
        if 'id' in data:
            id = data['id']
        comment = None
        if 'comment' in data:
            comment = data['comment']

        return self._create_span(offsets, type, attributes, normalizations, id, comment)

    def _create_span(self, offsets, _type, attributes=None, normalizations=None, _id=None, comment=None):
        if self._offset_overlaps(offsets):
            raise SpanOffsetOverlapError(offsets)

        undo_resp = {}

        _attributes = self._parse_attributes(attributes)
        _normalizations = self._parse_span_normalizations(normalizations)

        mods = ModificationTracker()

        if _id is not None:
            # We are to edit an existing annotation
            tb_ann, e_ann = self._edit_span(mods, _id, offsets, _attributes, _type, undo_resp=undo_resp)
        else:
            # We are to create a new annotation
            tb_ann, e_ann = self.__create_span(mods, _type, offsets, _attributes)

            undo_resp['action'] = 'add_tb'
            if e_ann is not None:
                undo_resp['id'] = e_ann.id
            else:
                undo_resp['id'] = tb_ann.id

        # Determine which annotation attributes, normalizations,
        # comments etc. should be attached to. If there's an event,
        # attach to that; otherwise attach to the textbound.
        if e_ann is not None:
            # Assign to the event, not the trigger
            target_ann = e_ann
        else:
            target_ann = tb_ann

        # Set attributes
        self._set_attributes(target_ann, _attributes, mods,
                        undo_resp=undo_resp)

        # Set normalizations
        self._set_normalizations(target_ann, _normalizations, mods,
                            undo_resp=undo_resp)

        # Set comments
        if tb_ann is not None:
            self._set_comments(target_ann, comment, mods,
                          undo_resp=undo_resp)

        if tb_ann is not None:
            mods_json = mods.json_response()
        else:
            # Hack, probably we had a new-line in the span
            mods_json = {}
            Messager.error('Text span contained new-line, rejected', duration=3)

        if undo_resp:
            mods_json['undo'] = json.dumps(undo_resp)
        mods_json['annotations'] = self._json_from_ann()
        return mods_json

    # Sanity check, a span can't overlap itself
    def _offset_overlaps(self, offsets):
        for i in range(0, len(offsets)):
            i_start, i_end = offsets[i]
            for j in range(i + 1, len(offsets)):
                j_start, j_end = offsets[j]
                if (
                        # i overlapping or in j
                                    (j_start <= i_start < j_end) or (j_start < i_end < j_end)
                            or
                            # j overlapping or in i
                                (i_start <= j_start < i_end) or (i_start < j_end < i_end)
                ):
                    return True
        # No overlap detected
        return False

    # helper for _create methods
    def _parse_attributes(self, attributes):
        if attributes is None:
            _attributes = {}
        else:
            try:
                _attributes = json.loads(attributes)
            except ValueError:
                # Failed to parse, warn the client
                Messager.warning((u'Unable to parse attributes string "%s" for '
                                  u'"createSpan", ignoring attributes for request and '
                                  u'assuming no attributes set') % (attributes,))
                _attributes = {}

            ### XXX: Hack since the client is sending back False and True as values...
            # These are __not__ to be sent, they violate the protocol
            for _del in [k for k, v in _attributes.items() if v == False]:
                del _attributes[_del]

            # These are to be old-style modifiers without values
            for _revalue in [k for k, v in _attributes.items() if v == True]:
                _attributes[_revalue] = True
                ###
        return _attributes

    # helper for _create_span
    def _parse_span_normalizations(self, normalizations):
        if normalizations is None:
            _normalizations = {}
        else:
            try:
                _normalizations = json.loads(normalizations)
            except ValueError:
                # Failed to parse, warn the client
                Messager.warning((u'Unable to parse normalizations string "%s" for '
                                  u'"createSpan", ignoring normalizations for request and '
                                  u'assuming no normalizations set') % (normalizations,))
                _normalizations = {}

        return _normalizations

    def __create_span(self, mods, type, offsets, attributes):
        # For event types, reuse trigger if a matching one exists.
        found = None
        if self.collection_configuration.is_event_type(type):
            for tb_ann in self.ann_obj.get_textbounds():
                try:
                    if (self._offsets_equal(tb_ann.spans, offsets)
                        and tb_ann.type == type):
                        found = tb_ann
                        break
                except AttributeError:
                    # Not a trigger then
                    pass

        if found is None:
            # Get a new ID
            new_id = self.ann_obj.get_new_id('T')  # XXX: Cons
            # Get the text span
            text_span = self._text_for_offsets(offsets)

            # The below code resolves cases where there are newlines in the
            #   offsets by creating discontinuous annotations for each span
            #   separated by newlines. For most cases it preserves the offsets.
            seg_offsets = []
            for o_start, o_end in offsets:
                pos = o_start
                for text_seg in text_span.split('\n'):
                    if not text_seg and o_start != o_end:
                        # Double new-line, skip ahead
                        pos += 1
                        continue
                    start = pos
                    end = start + len(text_seg)

                    # For the next iteration the position is after the newline.
                    pos = end + 1

                    # Adjust the offsets to compensate for any potential leading
                    #   and trailing whitespace.
                    start += len(text_seg) - len(text_seg.lstrip())
                    end -= len(text_seg) - len(text_seg.rstrip())

                    # If there is any segment left, add it to the offsets.
                    if start != end:
                        seg_offsets.append((start, end,))

            # if we're dealing with a null-span
            if not seg_offsets:
                seg_offsets = offsets

            ann_text = DISCONT_SEP.join((self.text[start:end]
                                         for start, end in seg_offsets))
            ann = TextBoundAnnotationWithText(seg_offsets, new_id, type, ann_text)
            self.ann_obj.add_annotation(ann)
            mods.addition(ann)
        else:
            ann = found

        if ann is not None:
            if self.collection_configuration.is_physical_entity_type(type):
                # TODO: alert that negation / speculation are ignored if set
                event = None
            else:
                # Create the event also
                new_event_id = self.ann_obj.get_new_id('E')  # XXX: Cons
                event = EventAnnotation(ann.id, [], str(new_event_id), type, '')
                self.ann_obj.add_annotation(event)
                mods.addition(event)
        else:
            # We got a newline in the span, don't take any action
            event = None

        return ann, event

    def _edit_span(self, mods, id, offsets, attributes, type, undo_resp={}):
        # TODO: Handle failure to find!
        ann = self.ann_obj.get_ann_by_id(id)

        if isinstance(ann, EventAnnotation):
            # We should actually modify the trigger
            tb_ann = self.ann_obj.get_ann_by_id(ann.trigger)
            e_ann = ann
            undo_resp['id'] = e_ann.id
            ann_category = EVENT_CATEGORY
        else:
            tb_ann = ann
            e_ann = None
            undo_resp['id'] = tb_ann.id
            ann_category = ENTITY_CATEGORY

        # Store away what we need to restore the old annotation
        undo_resp['action'] = 'mod_tb'
        undo_resp['offsets'] = tb_ann.spans[:]
        undo_resp['type'] = tb_ann.type

        if not self._offsets_equal(tb_ann.spans, offsets):
            if not isinstance(tb_ann, TextBoundAnnotation):
                # TODO XXX: the following comment is no longer valid
                # (possibly related code also) since the introduction of
                # TextBoundAnnotationWithText. Check.

                # This scenario has been discussed and changing the span inevitably
                # leads to the text span being out of sync since we can't for sure
                # determine where in the data format the text (if at all) it is
                # stored. For now we will fail loudly here.
                error_msg = ('unable to change the span of an existing annotation'
                             '(annotation: %s)' % repr(tb_ann))
                Messager.error(error_msg)
                # Not sure if we only get an internal server error or the data
                # will actually reach the client to be displayed.
                assert False, error_msg
            else:
                # TODO: Log modification too?
                before = str(tb_ann)
                # log_info('Will alter span of: "%s"' % str(to_edit_span).rstrip('\n'))
                tb_ann.spans = offsets[:]
                tb_ann.check_spans()
                tb_ann.text = self._text_for_offsets(tb_ann.spans)
                # log_info('Span altered')
                mods.change(before, tb_ann)

        if ann.type != type:
            if ann_category != self.collection_configuration.type_category(type):
                # Can't convert event to entity etc. (The client should protect
                # against this in any case.)
                # TODO: Raise some sort of protocol error
                Messager.error("Cannot convert %s (%s) into %s (%s)"
                               % (ann.type, self.collection_configuration.type_category(ann.type),
                                  type, self.collection_configuration.type_category(type)),
                               duration=10)
                pass
            else:
                before = str(ann)
                ann.type = type

                # Try to propagate the type change
                try:
                    # XXX: We don't take into consideration other anns with the
                    # same trigger here!
                    ann_trig = self.ann_obj.get_ann_by_id(ann.trigger)
                    if ann_trig.type != ann.type:
                        # At this stage we need to determine if someone else
                        # is using the same trigger
                        if any((event_ann
                                for event_ann in self.ann_obj.get_events()
                                if (event_ann.trigger == ann.trigger
                                    and event_ann != ann))):
                            # Someone else is using it, create a new one
                            from copy import copy
                            # A shallow copy should be enough
                            new_ann_trig = copy(ann_trig)
                            # It needs a new id
                            new_ann_trig.id = self.ann_obj.get_new_id('T')
                            # And we will change the type
                            new_ann_trig.type = ann.type
                            # Update the old annotation to use this trigger
                            ann.trigger = str(new_ann_trig.id)
                            self.ann_obj.add_annotation(new_ann_trig)
                            mods.addition(new_ann_trig)
                        else:
                            # Okay, we own the current trigger, but does an
                            # identical to our sought one already exist?
                            found = None
                            for tb_ann in self.ann_obj.get_textbounds():
                                if (self._offsets_equal(tb_ann.spans, ann_trig.spans) and
                                            tb_ann.type == ann.type):
                                    found = tb_ann
                                    break

                            if found is None:
                                # Just change the trigger type since we are the
                                # only users
                                before = str(ann_trig)
                                ann_trig.type = ann.type
                                mods.change(before, ann_trig)
                            else:
                                # Attach the new trigger THEN delete
                                # or the dep will hit you
                                ann.trigger = str(found.id)
                                self.ann_obj.del_annotation(ann_trig)
                                mods.deletion(ann_trig)
                except AttributeError:
                    # It was most likely a TextBound entity
                    pass

                # Finally remember the change
                mods.change(before, ann)
        return tb_ann, e_ann

    def _set_attributes(self, ann, attributes, mods, undo_resp={}):
        # Find existing attributes (if any)
        existing_attr_anns = set((a for a in self.ann_obj.get_attributes()
                                  if a.target == ann.id))

        # log_info('ATTR: %s' %(existing_attr_anns, ))

        # Note the existing annotations for undo
        undo_resp['attributes'] = json.dumps(dict([(e.type, e.value)
                                                   for e in existing_attr_anns]))

        for existing_attr_ann in existing_attr_anns:
            if existing_attr_ann.type not in attributes:
                # Delete attributes that were un-set existed previously
                self.ann_obj.del_annotation(existing_attr_ann)
                mods.deletion(existing_attr_ann)
            else:
                # If the value of the attribute is different, alter it
                new_value = attributes[existing_attr_ann.type]
                # log_info('ATTR: "%s" "%s"' % (new_value, existing_attr_ann.value))
                if existing_attr_ann.value != new_value:
                    before = str(existing_attr_ann)
                    existing_attr_ann.value = new_value
                    mods.change(before, existing_attr_ann)

        # The remaining annotations are new and should be created
        for attr_type, attr_val in attributes.items():
            if attr_type not in set((a.type for a in existing_attr_anns)):
                new_attr = AttributeAnnotation(ann.id, self.ann_obj.get_new_id('A'),
                                               attr_type, '', attr_val)
                self.ann_obj.add_annotation(new_attr)
                mods.addition(new_attr)


    def _set_normalizations(self, ann, normalizations, mods, undo_resp={}):
        # Find existing normalizations (if any)
        existing_norm_anns = set((a for a in self.ann_obj.get_normalizations()
                                  if a.target == ann.id))

        # Note the existing annotations for undo
        undo_resp['normalizations'] = json.dumps([(n.refdb, n.refid, n.reftext)
                                                  for n in existing_norm_anns])

        # Organize into dictionaries for easier access
        old_norms = dict([((n.refdb, n.refid), n) for n in existing_norm_anns])
        new_norms = dict([((n[0], n[1]), n[2]) for n in normalizations])

        # Messager.info("Old norms: "+str(old_norms))
        # Messager.info("New norms: "+str(new_norms))

        # sanity check
        for refdb, refid, refstr in normalizations:
            # TODO: less aggressive failure
            assert refdb is not None and refdb.strip() != '', "Error: client sent empty norm DB"
            assert refid is not None and refid.strip() != '', "Error: client sent empty norm ID"
            # (the reference string is allwed to be empty)

        # Process deletions and updates of existing normalizations
        for old_norm_id, old_norm in old_norms.items():
            if old_norm_id not in new_norms:
                # Delete IDs that were referenced previously but not anymore
                self.ann_obj.del_annotation(old_norm)
                mods.deletion(old_norm)
            else:
                # If the text value of the normalizations is different, update
                # (this shouldn't happen on a stable norm DB, but anyway)
                new_reftext = new_norms[old_norm_id]
                if old_norm.reftext != new_reftext:
                    old = str(old_norm)
                    old_norm.reftext = new_reftext
                    mods.change(old, old_norm)

        # Process new normalizations
        for new_norm_id, new_reftext in new_norms.items():
            if new_norm_id not in old_norms:
                new_id = self.ann_obj.get_new_id('N')
                # TODO: avoid magic string value
                norm_type = u'Reference'
                new_norm = NormalizationAnnotation(new_id, norm_type,
                                                   ann.id, new_norm_id[0],
                                                   new_norm_id[1],
                                                   u'\t' + new_reftext)
                self.ann_obj.add_annotation(new_norm)
                mods.addition(new_norm)

    # Helper for _create functions
    def _set_comments(self, ann, comment, mods, undo_resp={}):
        # We are only interested in id;ed comments
        try:
            ann.id
        except AttributeError:
            return None

        # Check if there is already an annotation comment
        for com_ann in self.ann_obj.get_oneline_comments():
            if (com_ann.type == 'AnnotatorNotes'
                and com_ann.target == ann.id):
                found = com_ann

                # Note the comment in the undo
                undo_resp['comment'] = found.tail[1:]
                break
        else:
            found = None

        if comment:
            if found is not None:
                # Change the comment
                # XXX: Note the ugly tab, it is for parsing the tail
                before = str(found)
                found.tail = u'\t' + comment
                mods.change(before, found)
            else:
                # Create a new comment
                new_comment = OnelineCommentAnnotation(
                    ann.id, self.ann_obj.get_new_id('#'),
                    # XXX: Note the ugly tab
                    u'AnnotatorNotes', u'\t' + comment)
                self.ann_obj.add_annotation(new_comment)
                mods.addition(new_comment)
        else:
            # We are to erase the annotation
            if found is not None:
                self.ann_obj.del_annotation(found)
                mods.deletion(found)

    def _enrich_json_with_text(self, j_dic):
        j_dic['text'] = self.text

        if(len(self.token_offsets) > 0 ):
            j_dic['token_offsets'] = self.token_offsets

        if(len(self.sentence_offsets) > 0 ):
            j_dic['sentence_offsets'] = self.sentence_offsets

        return True

    def _enrich_json_with_data(self, j_dic):
        # TODO: figure out if there's a reason for all the str()
        # invocations here; remove if not.

        # We collect trigger ids to be able to link the textbound later on
        trigger_ids = set()
        for event_ann in self.ann_obj.get_events():
            trigger_ids.add(event_ann.trigger)
            j_dic['events'].append(
                [str(event_ann.id), str(event_ann.trigger), event_ann.args]
            )

        for rel_ann in self.ann_obj.get_relations():
            j_dic['relations'].append(
                [str(rel_ann.id), str(rel_ann.type),
                 [(rel_ann.arg1l, rel_ann.arg1),
                  (rel_ann.arg2l, rel_ann.arg2)]]
            )

        for tb_ann in self.ann_obj.get_textbounds():
            # j_tb = [str(tb_ann.id), tb_ann.type, tb_ann.start, tb_ann.end]
            j_tb = [str(tb_ann.id), tb_ann.type, tb_ann.spans]

            # If we spotted it in the previous pass as a trigger for an
            # event or if the type is known to be an event type, we add it
            # as a json trigger.
            # TODO: proper handling of disconnected triggers. Currently
            # these will be erroneously passed as 'entities'
            if str(tb_ann.id) in trigger_ids:
                j_dic['triggers'].append(j_tb)
                # special case for BioNLP ST 2013 format: send triggers
                # also as entities for those triggers that are referenced
                # from annotations other than events (#926).
                if ALLOW_RELATIONS_REFERENCE_EVENT_TRIGGERS:
                    if tb_ann.id in self.ann_obj.externally_referenced_triggers:
                        try:
                            j_dic['entities'].append(j_tb)
                        except KeyError:
                            j_dic['entities'] = [j_tb, ]
            else:
                try:
                    j_dic['entities'].append(j_tb)
                except KeyError:
                    j_dic['entities'] = [j_tb, ]

        for eq_ann in self.ann_obj.get_equivs():
            j_dic['equivs'].append(
                (['*', eq_ann.type]
                 + [e for e in eq_ann.entities])
            )

        for att_ann in self.ann_obj.get_attributes():
            j_dic['attributes'].append(
                [str(att_ann.id), str(att_ann.type), str(att_ann.target), att_ann.value]
            )

        for norm_ann in self.ann_obj.get_normalizations():
            j_dic['normalizations'].append(
                [str(norm_ann.id), str(norm_ann.type),
                 str(norm_ann.target), str(norm_ann.refdb),
                 str(norm_ann.refid), str(norm_ann.reftext)]
            )

        for com_ann in self.ann_obj.get_oneline_comments():
            comment = [str(com_ann.target), str(com_ann.type),
                       com_ann.tail.strip()]
            try:
                j_dic['comments'].append(comment)
            except KeyError:
                j_dic['comments'] = [comment, ]

        if self.ann_obj.failed_lines:
            error_msg = 'Unable to parse the following line(s):\n%s' % (
                '\n'.join(
                    [('%s: %s' % (
                        # The line number is off by one
                        str(line_num + 1),
                        str(self.ann_obj[line_num])
                    )).strip()
                     for line_num in self.ann_obj.failed_lines])
            )
            Messager.error(error_msg, duration=len(self.ann_obj.failed_lines) * 3)

        j_dic['mtime'] = self.ann_obj.ann_mtime
        j_dic['ctime'] = self.ann_obj.ann_ctime

        try:
            issues = verify_annotation(self.ann_obj, self.collection_configuration)
        except Exception as e:
            # TODO add an issue about the failure?
            issues = []
            Messager.error(f'Error: verify_annotation() failed: {e}', -1)

        for i in issues:
            issue = (str(i.ann_id), i.type, i.description)
            try:
                j_dic['comments'].append(issue)
            except:
                j_dic['comments'] = [issue, ]

    def _text_for_offsets(self, offsets):
        """
        Given a text and a list of (start, end) integer offsets, returns
        the (catenated) text corresponding to those offsets, joined
        appropriately for use in a TextBoundAnnotation(WithText).
        """
        try:
            return DISCONT_SEP.join(self.text[s:e] for s, e in offsets)
        except Exception:
            Messager.error('_text_for_offsets: failed to get text for given offsets (%s)' % str(offsets))
            raise ProtocolArgumentError()

    def _offsets_equal(self, o1, o2):
        """
        Given two lists of (start, end) integer offset sets, returns
        whether they identify the same sets of characters.
        """
        # TODO: full implementation; current doesn't check for special
        # cases such as dup or overlapping (start, end) pairs in a single
        # set.

        # short-circuit (expected to be the most common case)
        if o1 == o2:
            return True
        return sorted(o1) == sorted(o2)

    def _enrich_json_with_base(self, j_dic):
        # TODO: Make the names here and the ones in the Annotations object conform

        # TODO: "from offset" of what? Commented this out, remove once
        # sure that nothing is actually using this.
        #     # This is the from offset
        #     j_dic['offset'] = 0

        for d in (
                'entities',
                'events',
                'relations',
                'triggers',
                'modifications',
                'attributes',
                'equivs',
                'normalizations',
                'comments',
        ):
            j_dic[d] = []

    def _json_from_ann(self):
        # Returns json with ann_obj contents and the relevant text.  Used
        # for saving a round-trip when modifying annotations by attaching
        # the latest annotation data into the response to the edit
        # request.
        j_dic = {}
        self._enrich_json_with_base(j_dic)
        self._enrich_json_with_text(j_dic)
        self._enrich_json_with_data(j_dic)
        return j_dic

    # TODO: ONLY determine what action to take! Delegate to Annotations!
    def delete_span(self, id):
        mods = ModificationTracker()

        # TODO: Handle a failure to find it
        # XXX: Slow, O(2N)
        ann = self.ann_obj.get_ann_by_id(id)
        try:
            # Note: need to pass the tracker to del_annotation to track
            # recursive deletes. TODO: make usage consistent.
            self.ann_obj.del_annotation(ann, mods)
            try:
                trig = self.ann_obj.get_ann_by_id(ann.trigger)
                try:
                    self.ann_obj.del_annotation(trig, mods)
                except DependingAnnotationDeleteError:
                    # Someone else depended on that trigger
                    pass
            except AttributeError:
                pass
        except DependingAnnotationDeleteError as e:
            Messager.error(e.html_error_str())
            return {
                'exception': True,
            }

        mods_json = mods.json_response()
        mods_json['annotations'] = self._json_from_ann()
        return mods_json

    def create_arc(self, data):
        origin = data['origin']
        target = data['target']
        type = data['type']
        attributes = None
        if 'attributes' in data:
            attributes = data['attributes']
        old_type = None
        if 'old_type' in data:
            old_type = data['old_type']
        old_target = None
        if 'old_target' in data:
            old_target = data['old_target']
        comment = None
        if 'comment' in data:
            comment = data['comment']

        return self._create_arc(origin, target, type, attributes, old_type, old_target, comment)

    # TODO: undo support
    def _create_arc(self, origin, target, type, attributes=None,
                   old_type=None, old_target=None, comment=None):
        undo_resp = {}

        mods = ModificationTracker()

        origin = self.ann_obj.get_ann_by_id(origin)
        target = self.ann_obj.get_ann_by_id(target)

        # if there is a previous annotation and the arcs aren't in
        # the same category (e.g. relation vs. event arg), process
        # as delete + create instead of update.
        if old_type is not None and (
                        self.collection_configuration.is_relation_type(old_type) !=
                        self.collection_configuration.is_relation_type(type) or
                        self.collection_configuration.is_equiv_type(old_type) !=
                        self.collection_configuration.is_equiv_type(type)):
            self._delete_arc_with_ann(origin.id, old_target, old_type, mods)
            old_target, old_type = None, None

        if self.collection_configuration.is_equiv_type(type):
            ann = self._create_equiv(mods, origin, target,
                                type, attributes, old_type, old_target)

        elif self.collection_configuration.is_relation_type(type):
            ann = self._create_relation(mods, origin, target,
                                   type, attributes, old_type, old_target)
        else:
            ann = self._create_argument(mods, origin, target,
                                   type, attributes, old_type, old_target)

        # process comments
        if ann is not None:
            self._set_comments(ann, comment, mods,
                          undo_resp=undo_resp)
        elif comment is not None:
            Messager.warning('create_arc: non-empty comment for None annotation (unsupported type for comment?)')

        mods_json = mods.json_response()
        mods_json['annotations'] = self._json_from_ann()
        return mods_json

    def _delete_arc_with_ann(self, origin, target, type_, mods):
        origin_ann = self.ann_obj.get_ann_by_id(origin)

        # specifics of delete determined by arc type (equiv relation,
        # other relation, event argument)
        if self.collection_configuration.is_relation_type(type_):
            if self.collection_configuration.is_equiv_type(type_):
                self._delete_arc_equiv(origin, target, type_, mods)
            else:
                self._delete_arc_nonequiv_rel(origin, target, type_, mods)
        elif self.collection_configuration.is_event_type(origin_ann.type):
            self._delete_arc_event_arg(origin, target, type_, mods)
        else:
            Messager.error('Unknown annotation types for delete')

    # helper for delete_arc
    def _delete_arc_equiv(self, origin, target, type_, mods):
        # TODO: this is slow, we should have a better accessor
        for eq_ann in self.ann_obj.get_equivs():
            # We don't assume that the ids only occur in one Equiv, we
            # keep on going since the data "could" be corrupted
            if (str(origin) in eq_ann.entities and
                        str(target) in eq_ann.entities and
                        type_ == eq_ann.type):
                before = str(eq_ann)
                eq_ann.entities.remove(str(origin))
                eq_ann.entities.remove(str(target))
                mods.change(before, eq_ann)

            if len(eq_ann.entities) < 2:
                # We need to delete this one
                try:
                    self.ann_obj.del_annotation(eq_ann)
                    mods.deletion(eq_ann)
                except DependingAnnotationDeleteError as e:
                    # TODO: This should never happen, dep on equiv
                    raise

                    # TODO: warn on failure to delete?

    # helper for delete_arc
    def _delete_arc_nonequiv_rel(self, origin, target, type_, mods):
        # TODO: this is slow, we should have a better accessor
        for ann in self.ann_obj.get_relations():
            if ann.type == type_ and ann.arg1 == origin and ann.arg2 == target:
                self.ann_obj.del_annotation(ann)
                mods.deletion(ann)

                # TODO: warn on failure to delete?

    # helper for delete_arc
    def _delete_arc_event_arg(self, origin, target, type_, mods):
        event_ann = self.ann_obj.get_ann_by_id(origin)
        # Try if it is an event
        arg_tup = (type_, str(target))
        if arg_tup in event_ann.args:
            before = str(event_ann)
            event_ann.args.remove(arg_tup)
            mods.change(before, event_ann)
        else:
            # What we were to remove did not even exist in the first place
            # TODO: warn on failure to delete?
            pass

    def _create_equiv(self, mods, origin, target, type, attributes,
                      old_type, old_target):
        # due to legacy representation choices for Equivs (i.e. no
        # unique ID), support for attributes for Equivs would need
        # some extra work. Getting the easy non-Equiv case first.
        if attributes is not None:
            Messager.warning(
                '_create_equiv: attributes for Equiv annotation not supported yet, please tell the devs if you need this feature (mention "issue #799").')
            attributes = None

        ann = None

        if old_type is None:
            # new annotation

            # sanity
            assert old_target is None, '_create_equiv: incoherent args: old_type is None, old_target is not None (client/protocol error?)'

            ann = EquivAnnotation(type, [str(origin.id),
                                         str(target.id)], '')
            self.ann_obj.add_annotation(ann)
            mods.addition(ann)

            # TODO: attributes
            assert attributes is None, "INTERNAL ERROR"  # see above
        else:
            # change to existing Equiv annotation. Other than the no-op
            # case, this remains TODO.
            assert self.collection_configuration.is_equiv_type(
                old_type), 'attempting to change equiv relation to non-equiv relation, operation not supported'

            # sanity
            assert old_target is not None, '_create_equiv: incoherent args: old_type is not None, old_target is None (client/protocol error?)'

            if old_type != type:
                Messager.warning(
                    '_create_equiv: equiv type change not supported yet, please tell the devs if you need this feature (mention "issue #798").')

            if old_target != target.id:
                Messager.warning(
                    '_create_equiv: equiv reselect not supported yet, please tell the devs if you need this feature (mention "issue #797").')

            # TODO: attributes
            assert attributes is None, "INTERNAL ERROR"  # see above

        return ann

    def _create_relation(self, mods, origin, target, type,
                         attributes, old_type, old_target, undo_resp={}):
        attributes = self._parse_attributes(attributes)

        if old_type is not None or old_target is not None:
            assert type in self.collection_configuration.get_relation_types(), (
                ('attempting to convert relation to non-relation "%s" ' % (target.type,)) +
                ('(legit types: %s)' % (str(self.collection_configuration.get_relation_types()),)))

            sought_target = (old_target
                             if old_target is not None else target.id)
            sought_type = (old_type
                           if old_type is not None else type)
            sought_origin = origin.id

            # We are to change the type, target, and/or attributes
            found = None
            for ann in self.ann_obj.get_relations():
                if (ann.arg1 == sought_origin and ann.arg2 == sought_target and
                            ann.type == sought_type):
                    found = ann
                    break

            if found is None:
                # TODO: better response
                Messager.error('_create_relation: failed to identify target relation (type %s, target %s) (deleted?)' % (
                str(old_type), str(old_target)))
            elif found.arg2 == target.id and found.type == type:
                # no changes to type or target
                pass
            else:
                # type and/or target changed, mark.
                before = str(found)
                found.arg2 = target.id
                found.type = type
                mods.change(before, found)

            target_ann = found
        else:
            # Create a new annotation
            new_id = self.ann_obj.get_new_id('R')
            # TODO: do we need to support different relation arg labels
            # depending on participant types? This doesn't.
            rels = self.collection_configuration.get_relations_by_type(type)
            rel = rels[0] if rels else None
            assert rel is not None and len(rel['args']) == 2
            a1l = rel['args'][0]['role']
            a2l = rel['args'][1]['role']
            ann = BinaryRelationAnnotation(new_id, type, a1l, origin.id, a2l, target.id, '\t')
            mods.addition(ann)
            self.ann_obj.add_annotation(ann)

            target_ann = ann

        # process attributes
        if target_ann is not None:
            self._set_attributes(target_ann, attributes, mods, undo_resp)
        elif attributes != None:
            Messager.error(
                '_create_relation: cannot set arguments: failed to identify target relation (type %s, target %s) (deleted?)' % (
                str(old_type), str(old_target)))

        return target_ann

    def _create_argument(self, mods, origin, target, type,
                         attributes, old_type, old_target):
        try:
            arg_tup = (type, str(target.id))

            # Is this an addition or an update?
            if old_type is None and old_target is None:
                if arg_tup not in origin.args:
                    before = str(origin)
                    origin.add_argument(type, str(target.id))
                    mods.change(before, origin)
                else:
                    # It already existed as an arg, we were called to do nothing...
                    pass
            else:
                # Construct how the old arg would have looked like
                old_arg_tup = (type if old_type is None else old_type,
                               target if old_target is None else old_target)

                if old_arg_tup in origin.args and arg_tup not in origin.args:
                    before = str(origin)
                    origin.args.remove(old_arg_tup)
                    origin.add_argument(type, str(target.id))
                    mods.change(before, origin)
                else:
                    # Collision etc. don't do anything
                    pass
        except AttributeError:
            # The annotation did not have args, it was most likely an entity
            # thus we need to create a new Event...
            new_id = self.ann_obj.get_new_id('E')
            ann = EventAnnotation(
                origin.id,
                [arg_tup],
                new_id,
                origin.type,
                ''
            )
            self.ann_obj.add_annotation(ann)
            mods.addition(ann)

        # No addressing mechanism for arguments at the moment
        return None

    def delete_arc(self, origin, target, type):
        mods = ModificationTracker()

        self._delete_arc_with_ann(origin, target, type, mods)

        mods_json = mods.json_response()
        mods_json['annotations'] = self._json_from_ann()
        return mods_json

        # TODO: error handling?

    def reverse_arc(self, origin, target, type, attributes=None):
        # undo_resp = {} # TODO
        # mods = ModificationTracker() # TODO
        if self.collection_configuration.is_equiv_type(type):
            Messager.warning('Cannot reverse Equiv arc')
        elif not self.collection_configuration.is_relation_type(type):
            Messager.warning('Can only reverse configured binary relations')
        else:
            # OK to reverse
            found = None
            # TODO: more sensible lookup
            for ann in self.ann_obj.get_relations():
                if (ann.arg1 == origin and ann.arg2 == target and
                            ann.type == type):
                    found = ann
                    break
            if found is None:
                Messager.error('reverse_arc: failed to identify target relation (from %s to %s, type %s) (deleted?)' % (
                str(origin), str(target), str(type)))
            else:
                # found it; just adjust this
                found.arg1, found.arg2 = found.arg2, found.arg1
                # TODO: modification tracker

        json_response = {}
        json_response['annotations'] = self._json_from_ann()
        return json_response


class ModificationTracker(object):
    def __init__(self):
        self.__added = []
        self.__changed = []
        self.__deleted = []

    def __len__(self):
        return len(self.__added) + len(self.__changed) + len(self.__deleted)

    def addition(self, added):
        self.__added.append(added)

    def deletion(self, deleted):
        self.__deleted.append(deleted)

    def change(self, before, after):
        self.__changed.append((before, after))

    def json_response(self, response=None):
        if response is None:
            response = {}

        # debugging
        if DEBUG:
            msg_str = ''
            if self.__added:
                msg_str += ('Added the following line(s):\n'
                        + '\n'.join([str(a).rstrip() for a in self.__added]))
            if self.__changed:
                changed_strs = []
                for before, after in self.__changed:
                    changed_strs.append('\t%s\n\tInto:\n\t%s' % (str(before).rstrip(), str(after).rstrip()))
                msg_str += ('Changed the following line(s):\n'
                        + '\n'.join([str(a).rstrip() for a in changed_strs]))
            if self.__deleted:
                msg_str += ('Deleted the following line(s):\n'
                        + '\n'.join([str(a).rstrip() for a in self.__deleted]))
            if msg_str:
                Messager.info(msg_str, duration=3*len(self))
            else:
                Messager.info('No changes made')

        # highlighting
        response['edited'] = []
        # TODO: implement cleanly, e.g. add a highlightid() method to Annotation classes
        for a in self.__added:
            try:
                response['edited'].append(a.reference_id())
            except AttributeError:
                pass  # not all implement reference_id()
        for b, a in self.__changed:
            # can't mark "before" since it's stopped existing
            try:
                response['edited'].append(a.reference_id())
            except AttributeError:
                pass  # not all implement reference_id()

        # unique, preserve order
        seen = set()
        uniqued = []
        for i in response['edited']:
            s = str(i)
            if s not in seen:
                uniqued.append(i)
                seen.add(s)
        response['edited'] = uniqued

        return response


class SpanOffsetOverlapError(ProtocolError):
    def __init__(self, offsets):
        self.offsets = offsets

    def __str__(self):
        offsetsStr = (', '.join(str(e) for e in self.offsets, ))
        return f'The offsets {offsetsStr} overlap'

    def json(self, json_dic):
        json_dic['exception'] = 'spanOffsetOverlapError'
        return json_dic
