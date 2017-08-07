# coding=utf-8
from codecs import open as codecs_open
from itertools import chain, takewhile
from time import time
from re import match as re_match

from brat_widget.common import ProtocolError
from brat_widget.messager import Messager

# String used to catenate texts of discontinuous annotations in reference text
DISCONT_SEP = ' '
ALLOW_RELATIONS_REFERENCE_EVENT_TRIGGERS = True



class AnnotationLineSyntaxError(Exception):
    def __init__(self, line, line_num, filepath):
        self.line = line
        self.line_num = line_num
        self.filepath = filepath

    def __str__(self):
        u'Syntax error on line %d: "%s"' % (self.line_num, self.line)


class IdedAnnotationLineSyntaxError(AnnotationLineSyntaxError):
    def __init__(self, id, line, line_num, filepath):
        AnnotationLineSyntaxError.__init__(self, line, line_num, filepath)
        self.id = id

    def __str__(self):
        u'Syntax error on line %d (id %s): "%s"' % (self.line_num, self.id, self.line)


class AnnotationNotFoundError(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return u'Could not find an annotation with id: %s' % (self.id,)


class EventWithoutTriggerError(ProtocolError):
    def __init__(self, event):
        self.event = event

    def __str__(self):
        return u'Event "%s" lacks a trigger' % (self.event,)

    def json(self, json_dic):
        json_dic['exception'] = 'eventWithoutTrigger'
        return json_dic


class EventWithNonTriggerError(ProtocolError):
    def __init__(self, event, non_trigger):
        self.event = event
        self.non_trigger = non_trigger

    def __str__(self):
        return u'Non-trigger "%s" used by "%s" as trigger' % (
            self.non_trigger, self.event,)

    def json(self, json_dic):
        json_dic['exception'] = 'eventWithNonTrigger'
        return json_dic


class TriggerReferenceError(ProtocolError):
    def __init__(self, trigger, referencer):
        self.trigger = trigger
        self.referencer = referencer

    def __str__(self):
        return u'Trigger "%s" referenced by non-event "%s"' % (self.trigger,
                                                               self.referencer,)

    def json(self, json_dic):
        json_dic['exception'] = 'triggerReference'
        return json_dic


class DuplicateAnnotationIdError(AnnotationLineSyntaxError):
    def __init__(self, id, line, line_num, filepath):
        AnnotationLineSyntaxError.__init__(self, line, line_num, filepath)
        self.id = id

    def __str__(self):
        return (u'Duplicate id: %s on line %d (id %s): "%s"'
                ) % (self.id, self.line_num, self.id, self.line)


class InvalidIdError(Exception):
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return u'Invalid id: %s' % (self.id,)


class DependingAnnotationDeleteError(Exception):
    def __init__(self, target, dependants):
        self.target = target
        self.dependants = dependants

    def __str__(self):
        return u'%s can not be deleted due to depending annotations %s' % (
            str(self.target).rstrip(), ",".join([str(d).rstrip() for d in self.dependants]))

    def html_error_str(self, response=None):
        return u'''Annotation:
        %s
        Has depending annotations attached to it:
        %s''' % (str(self.target).rstrip(), ",".join([str(d).rstrip() for d in self.dependants]))


def __split_annotation_id(id):
    m = re_match(r'^([A-Za-z]+|#[A-Za-z]*)([0-9]+)(.*?)$', id)
    if m is None:
        raise InvalidIdError(id)
    pre, num_str, suf = m.groups()
    return pre, num_str, suf


def annotation_id_prefix(id):
    pre = ''.join(c for c in takewhile(lambda x: not x.isdigit(), id))
    if not pre:
        raise InvalidIdError(id)
    return pre


def annotation_id_number(id):
    return __split_annotation_id(id)[1]


def is_valid_id(id):
    # special case: '*' is acceptable as an "ID"
    if id == '*':
        return True

    try:
        # currently accepting any ID that can be split.
        # TODO: consider further constraints
        __split_annotation_id(id)[1]
        return True
    except InvalidIdError:
        return False


class Annotations(object):
    """
    Basic annotation storage. Not concerned with conformity of
    annotations to text; can be created without access to the
    text file to which the annotations apply.
    """

    def __init__(self, document):
        from collections import defaultdict

        # we should remember this
        self._document = document

        self.failed_lines = []
        self.externally_referenced_triggers = set()

        ### Here be dragons, these objects need constant updating and syncing
        # Annotation for each line of the file
        self._lines = []
        # Mapping between annotation objects and which line they occur on
        # Range: [0, inf.) unlike [1, inf.) which is common for files
        self._line_by_ann = {}
        # Maximum id number used for each id prefix, to speed up id generation
        # XXX: This is effectively broken by the introduction of id suffixes
        self._max_id_num_by_prefix = defaultdict(lambda: 1)
        # Annotation by id, not includid non-ided annotations
        self._ann_by_id = {}
        ###

        # Finally, parse the given annotation file
        try:
            for l in self._document.entities:
                self.add_annotation(TextBoundAnnotationWithText.from_list(l, self))
            for l in self._document.relations:
                self.add_annotation(BinaryRelationAnnotation.from_list(l, self))
            for l in self._document.events:
                self.add_annotation(EventAnnotation.from_list(l, self))
            for l in self._document.comments:
                self.add_annotation(OnelineCommentAnnotation.from_list(l, self))
            for l in self._document.attributes:
                self.add_annotation(AttributeAnnotation.from_list(l, self))
            for l in self._document.equivs:
                self.add_annotation(EquivAnnotation.from_list(l, self))
            for l in self._document.normalizations:
                self.add_annotation(NormalizationAnnotation.from_list(l, self))

            # Sanity checking that can only be done post-parse
            self._sanity()
        except Exception as l:
            Messager.error('Encoding error reading annotation file: '
                           'nonstandard encoding or binary?', -1)
            # TODO: more specific exception
            raise l

        self.ann_mtime = self._document.mtime
        self.ann_ctime = self._document.ctime

    def _sanity(self):
        # Beware, we ONLY do format checking, leave your semantics hat at home

        # Check that referenced IDs are defined
        for ann in self:
            for rid in chain(*ann.get_deps()):
                try:
                    self.get_ann_by_id(rid)
                except AnnotationNotFoundError:
                    # TODO: do more than just send a message for this error?
                    Messager.error('ID ' + rid + ' not defined, referenced from annotation ' + str(ann))

        # Check that each event has a trigger
        for e_ann in self.get_events():
            try:
                tr_ann = self.get_ann_by_id(e_ann.trigger)

                # If the annotation is not text-bound or of different type
                if (not isinstance(tr_ann, TextBoundAnnotation) or
                            tr_ann.type != e_ann.type):
                    raise EventWithNonTriggerError(e_ann, tr_ann)
            except AnnotationNotFoundError:
                raise EventWithoutTriggerError(e_ann)

        # Check that every trigger is only referenced by events

        # Create a map for non-event references
        referenced_to_referencer = {}
        for non_e_ann in (a for a in self
                          if not isinstance(a, EventAnnotation)
                          and isinstance(a, IdedAnnotation)):
            for ref in chain(*non_e_ann.get_deps()):
                try:
                    referenced_to_referencer[ref].add(non_e_ann.id)
                except KeyError:
                    referenced_to_referencer[ref] = set((non_e_ann.id,))

        # Ensure that no non-event references a trigger
        for tr_ann in self.get_triggers():
            if tr_ann.id in referenced_to_referencer:
                conflict_ann_ids = referenced_to_referencer[tr_ann.id]
                if ALLOW_RELATIONS_REFERENCE_EVENT_TRIGGERS:
                    # Special-case processing for BioNLP ST 2013: allow
                    # Relations to reference event triggers (#926).
                    remaining_confict_ann_ids = set()
                    for rid in conflict_ann_ids:
                        referencer = self.get_ann_by_id(rid)
                        if not isinstance(referencer, BinaryRelationAnnotation):
                            remaining_confict_ann_ids.add(rid)
                        else:
                            self.externally_referenced_triggers.add(tr_ann.id)
                    conflict_ann_ids = remaining_confict_ann_ids
                # Note: Only reporting one of the conflicts (TODO)
                if conflict_ann_ids:
                    referencer = self.get_ann_by_id(list(conflict_ann_ids)[0])
                    raise TriggerReferenceError(tr_ann, referencer)

    def get_events(self):
        return (a for a in self if isinstance(a, EventAnnotation))

    def get_attributes(self):
        return (a for a in self if isinstance(a, AttributeAnnotation))

    def get_equivs(self):
        return (a for a in self if isinstance(a, EquivAnnotation))

    def get_textbounds(self):
        return (a for a in self if isinstance(a, TextBoundAnnotation))

    def get_relations(self):
        return (a for a in self if isinstance(a, BinaryRelationAnnotation))

    def get_normalizations(self):
        return (a for a in self if isinstance(a, NormalizationAnnotation))

    def get_entities(self):
        # Entities are textbounds that are not triggers
        triggers = [t for t in self.get_triggers()]
        return (a for a in self if (isinstance(a, TextBoundAnnotation) and
                                    not a in triggers))

    def get_oneline_comments(self):
        # XXX: The status exception is for the document status protocol
        #       which is yet to be formalised
        return (a for a in self if isinstance(a, OnelineCommentAnnotation)
                and a.type != 'STATUS')

    def get_statuses(self):
        return (a for a in self if isinstance(a, OnelineCommentAnnotation)
                and a.type == 'STATUS')

    def get_triggers(self):
        # Triggers are text-bounds referenced by events
        # TODO: this omits entity triggers that lack a referencing event
        # (for one reason or another -- brat shouldn't define any.)
        return (self.get_ann_by_id(e.trigger) for e in self.get_events())

    # TODO: getters for other categories of annotations
    # TODO: Remove read and use an internal and external version instead
    def add_annotation(self, ann):
        # Equivs have to be merged with other equivs
        try:
            # Bail as soon as possible for non-equivs
            #ann.entities  # TODO: what is this?
            merge_cand = ann
            for eq_ann in self.get_equivs():
                try:
                    # Make sure that this Equiv duck quacks
                    eq_ann.entities
                except AttributeError as e:
                    assert False, 'got a non-entity from an entity call'

                # Do we have an entitiy in common with this equiv?
                for ent in merge_cand.entities:
                    if ent in eq_ann.entities:
                        for m_ent in merge_cand.entities:
                            if m_ent not in eq_ann.entities:
                                eq_ann.entities.append(m_ent)
                        # Don't try to delete ann since it never was added
                        if merge_cand != ann:
                            try:
                                self.del_annotation(merge_cand)
                            except DependingAnnotationDeleteError:
                                assert False, ('Equivs lack ids and should '
                                               'never have dependent annotations')
                        merge_cand = eq_ann
                        # We already merged it all, break to the next ann
                        break

            if merge_cand != ann:
                # The proposed annotation was simply merged, no need to add it
                # Update the modification time
                from time import time
                self.ann_mtime = time()
                return

        except AttributeError:
            # XXX: This can catch a ton more than we want to! Ugly!
            # It was not an Equiv, skip along
            pass

        # Register the object id
        try:
            self._ann_by_id[ann.id] = ann
            pre, num = annotation_id_prefix(ann.id), annotation_id_number(ann.id)
            self._max_id_num_by_prefix[pre] = max(int(num), self._max_id_num_by_prefix[pre])
        except AttributeError:
            # The annotation simply lacked an id which is fine
            pass

        # Add the annotation as the last line
        self._lines.append(ann)
        self._line_by_ann[ann] = len(self) - 1
        # Update the modification time
        from time import time
        self.ann_mtime = time()

    def del_annotation(self, ann, tracker=None):
        # TODO: Flag to allow recursion
        # TODO: Sampo wants to allow delet of direct deps but not indirect, one step
        # TODO: needed to pass tracker to track recursive mods, but use is too
        #      invasive (direct modification of ModificationTracker.deleted)
        # TODO: DOC!
        try:
            ann.id
        except AttributeError:
            # If it doesn't have an id, nothing can depend on it
            if tracker is not None:
                tracker.deletion(ann)
            self._atomic_del_annotation(ann)
            # Update the modification time
            from time import time
            self.ann_mtime = time()
            return

        # collect annotations dependending on ann
        ann_deps = []

        for other_ann in self:
            soft_deps, hard_deps = other_ann.get_deps()
            if str(ann.id) in soft_deps | hard_deps:
                ann_deps.append(other_ann)

        # If all depending are AttributeAnnotations or EquivAnnotations,
        # delete all modifiers recursively (without confirmation) and remove
        # the annotation id from the equivs (and remove the equiv if there is
        # only one id left in the equiv)
        # Note: this assumes AttributeAnnotations cannot have
        # other dependencies depending on them, nor can EquivAnnotations
        if all((False for d in ann_deps if (
                            not isinstance(d, AttributeAnnotation)
                        and not isinstance(d, EquivAnnotation)
                    and not isinstance(d, OnelineCommentAnnotation)
                and not isinstance(d, NormalizationAnnotation)
        ))):

            for d in ann_deps:
                if isinstance(d, AttributeAnnotation):
                    if tracker is not None:
                        tracker.deletion(d)
                    self._atomic_del_annotation(d)
                elif isinstance(d, EquivAnnotation):
                    if len(d.entities) <= 2:
                        # An equiv has to have more than one member
                        self._atomic_del_annotation(d)
                        if tracker is not None:
                            tracker.deletion(d)
                    else:
                        if tracker is not None:
                            before = str(d)
                        d.entities.remove(str(ann.id))
                        if tracker is not None:
                            tracker.change(before, d)
                elif isinstance(d, OnelineCommentAnnotation):
                    # TODO: Can't anything refer to comments?
                    self._atomic_del_annotation(d)
                    if tracker is not None:
                        tracker.deletion(d)
                elif isinstance(d, NormalizationAnnotation):
                    # Nothing should be able to reference normalizations
                    self._atomic_del_annotation(d)
                    if tracker is not None:
                        tracker.deletion(d)
                else:
                    # all types we allow to be deleted along with
                    # annotations they depend on should have been
                    # covered above.
                    assert False, "INTERNAL ERROR"
            ann_deps = []

        if ann_deps:
            raise DependingAnnotationDeleteError(ann, ann_deps)

        if tracker is not None:
            tracker.deletion(ann)
        self._atomic_del_annotation(ann)

    def _atomic_del_annotation(self, ann):
        # TODO: DOC
        # Erase the ann by id shorthand
        try:
            del self._ann_by_id[ann.id]
        except AttributeError:
            # So, we did not have id to erase in the first place
            pass

        ann_line = self._line_by_ann[ann]
        # Erase the main annotation
        del self._lines[ann_line]
        # Erase the ann by line shorthand
        del self._line_by_ann[ann]
        # Update the line shorthand of every annotation after this one
        # to reflect the new self._lines
        for l_num in range(ann_line, len(self)):
            self._line_by_ann[self[l_num]] = l_num
        # Update the modification time
        from time import time
        self.ann_mtime = time()

    def get_ann_by_id(self, id):
        # TODO: DOC
        try:
            return self._ann_by_id[id]
        except KeyError:
            raise AnnotationNotFoundError(id)

    def get_new_id(self, prefix, suffix=None):
        '''
        Return a new valid unique id for this annotation file for the given
        prefix. No ids are re-used for traceability over time for annotations,
        but this only holds for the lifetime of the annotation object. If the
        annotation file is parsed once again into an annotation object the
        next assigned id will be the maximum seen for a given prefix plus one
        which could have been deleted during a previous annotation session.

        Warning: get_new_id('T') == get_new_id('T')
        Just calling this method does not reserve the id, you need to
        add the annotation with the returned id to the annotation object in
        order to reserve it.

        Argument(s):
        id_pre - an annotation prefix on the format [A-Za-z]+

        Returns:
        An id that is guaranteed to be unique for the lifetime of the
        annotation.
        '''
        # XXX: We have changed this one radically!
        # XXX: Stupid and linear
        if suffix is None:
            suffix = ''
        # XXX: Arbitrary constant!
        for suggestion in (prefix + str(i) + suffix for i in range(1, 2 ** 15)):
            # This is getting more complicated by the minute, two checks since
            # the developers no longer know when it is an id or string.
            if suggestion not in self._ann_by_id:
                return suggestion

    def __str__(self):
        s = u'\n'.join(str(ann).rstrip(u'\r\n') for ann in self)
        if not s:
            return u''
        else:
            return s if s[-1] == u'\n' else s + u'\n'

    def __it__(self):
        for ann in self._lines:
            yield ann

    def __getitem__(self, val):
        try:
            # First, try to use it as a slice object
            return self._lines[val.start, val.stop, val.step]
        except AttributeError:
            # It appears not to be a slice object, try it as an index
            return self._lines[val]

    def __len__(self):
        return len(self._lines)

    def __in__(self, other):
        # XXX: You should do this one!
        pass


class TextAnnotations(Annotations):
    """
    Text-bound annotation storage. Extends Annotations in assuming
    access to text text to which the annotations apply and verifying
    the correctness of text-bound annotations against the text.
    """

    def __init__(self, document):
        Annotations.__init__(self, document)


class Annotation(object):
    """
    Base class for all annotations.
    """

    def __init__(self, tail, source_id=None):
        self.tail = tail
        self.source_id = source_id

    def __str__(self):
        raise NotImplementedError()

    def __repr__(self):
        return u'%s("%s")' % (str(self.__class__), str(self))

    def get_deps(self):
        return (set(), set())

    @classmethod
    def from_list(cls, list, annotations):
        raise NotImplementedError()

    def to_list(self):
        raise NotImplementedError()


class TypedAnnotation(Annotation):
    """
    Base class for all annotations with a type.
    """

    def __init__(self, type, tail, source_id=None):
        Annotation.__init__(self, tail, source_id=source_id)
        self.type = type

    def __str__(self):
        raise NotImplementedError


class IdedAnnotation(TypedAnnotation):
    """
    Base class for all annotations with an ID.
    """

    def __init__(self, id, type, tail, source_id=None):
        TypedAnnotation.__init__(self, type, tail, source_id=source_id)
        self.id = id

    def reference_id(self):
        """Returns a list that uniquely identifies this annotation within its document."""
        return [self.id]

    def reference_text(self):
        """Returns a human-readable string that identifies this annotation within its document."""
        return str(self.reference_id()[0])

    def __str__(self):
        raise NotImplementedError


def split_role(r):
    """
    Given a string R that may be suffixed with a number, returns a
    tuple (ROLE, NUM) where ROLE+NUM == R and NUM is the maximal
    suffix of R consisting only of digits.
    """
    i = len(r)
    while i > 1 and r[i - 1].isdigit():
        i -= 1
    return r[:i], r[i:]


class EventAnnotation(IdedAnnotation):
    """
    Represents an event annotation. Events are typed annotations that
    are associated with a specific text expression stating the event
    (TRIGGER, identifying a TextBoundAnnotation) and have an arbitrary
    number of arguments, each of which is represented as a ROLE:PARTID
    pair, where ROLE is a string identifying the role (e.g. "Theme",
    "Cause") and PARTID the ID of another annotation participating in
    the event.

    Represented in standoff as

    ID\tTYPE:TRIGGER [ROLE1:PART1 ROLE2:PART2 ...]
    """

    def __init__(self, trigger, args, id, type, tail, source_id=None):
        IdedAnnotation.__init__(self, id, type, tail, source_id=source_id)
        self.trigger = trigger
        self.args = args

    def add_argument(self, role, argid):
        # split into "main" role label and possible numeric suffix
        role, rnum = split_role(role)
        if rnum != '':
            # if given a role with an explicit numeric suffix,
            # use the role as given (assume number is part of
            # role label).
            pass
        else:
            # find next free numeric suffix.

            # for each argument role in existing roles, determine the
            # role numbers already used
            rnums = {}
            for r, aid in self.args:
                rb, rn = split_role(r)
                if rb not in rnums:
                    rnums[rb] = {}
                rnums[rb][rn] = True

            # find the first available free number for the current role,
            # using the convention that the empty number suffix stands for 1
            rnum = ''
            while role in rnums and rnum in rnums[role]:
                if rnum == '':
                    rnum = '2'
                else:
                    rnum = str(int(rnum) + 1)

        # role+rnum is available, add
        self.args.append((role + rnum, argid))

    def __str__(self):
        return u'%s\t%s:%s %s%s' % (
            self.id,
            self.type,
            self.trigger,
            ' '.join([':'.join(map(str, arg_tup))
                      for arg_tup in self.args]),
            self.tail
        )

    def get_deps(self):
        soft_deps, hard_deps = IdedAnnotation.get_deps(self)
        hard_deps.add(self.trigger)
        arg_ids = [arg_tup[1] for arg_tup in self.args]
        # TODO: verify this logic, it's not entirely clear it's right
        if len(arg_ids) > 1:
            for arg in arg_ids:
                soft_deps.add(arg)
        else:
            for arg in arg_ids:
                hard_deps.add(arg)
        return (soft_deps, hard_deps)

    @classmethod
    def from_list(cls, list, annotations):
        type = annotations.get_ann_by_id(list[1]).type
        return EventAnnotation(list[1], list[2], list[0], type, '\t')

    def to_list(self):
        return [self.id, self.trigger, self.args]


class EquivAnnotation(TypedAnnotation):
    """
    Represents an equivalence group annotation. Equivs define a set of
    other annotations (normally TextBoundAnnotation) to be equivalent.

    Represented in standoff as

    *\tTYPE ID1 ID2 [...]

    Where "*" is the literal asterisk character.
    """

    def __init__(self, type, entities, tail, source_id=None):
        TypedAnnotation.__init__(self, type, tail, source_id=source_id)
        self.entities = entities

    def __in__(self, other):
        return other in self.entities

    def __str__(self):
        return u'*\t%s %s%s' % (
            self.type,
            ' '.join([str(e) for e in self.entities]),
            self.tail
        )

    def get_deps(self):
        soft_deps, hard_deps = TypedAnnotation.get_deps(self)
        if len(self.entities) > 2:
            for ent in self.entities:
                soft_deps.add(ent)
        else:
            for ent in self.entities:
                hard_deps.add(ent)
        return (soft_deps, hard_deps)

    def reference_id(self):
        if self.entities:
            return ['equiv', self.type, self.entities[0]]
        else:
            return ['equiv', self.type, self.entities]

    def reference_text(self):
        return '(' + ','.join([str(e) for e in self.entities]) + ')'

    @classmethod
    def from_list(cls, list, annotations):
        return EquivAnnotation(list[1], list[2:], '')

    def to_list(self):
        return ['*', self.type] + self.entities


class AttributeAnnotation(IdedAnnotation):
    def __init__(self, target, id, type, tail, value, source_id=None):
        IdedAnnotation.__init__(self, id, type, tail, source_id=source_id)
        self.target = target
        self.value = value

    def __str__(self):
        return u'%s\t%s %s%s%s' % (
            self.id,
            self.type,
            self.target,
            # We hack in old modifiers with this trick using bools
            ' ' + str(self.value) if self.value != True else '',
            self.tail,
        )

    def get_deps(self):
        soft_deps, hard_deps = IdedAnnotation.get_deps(self)
        hard_deps.add(self.target)
        return (soft_deps, hard_deps)

    def reference_id(self):
        # TODO: can't currently ID modifier in isolation; return
        # reference to modified instead
        return [self.target]

    @classmethod
    def from_list(cls, list, annotations):
        return AttributeAnnotation(list[2], list[0], list[1], '', list[3])

    def to_list(self):
        return [self.id, self.type, self.target, self.value]


class NormalizationAnnotation(IdedAnnotation):
    def __init__(self, _id, _type, target, refdb, refid, tail, source_id=None):
        IdedAnnotation.__init__(self, _id, _type, tail, source_id=source_id)
        self.target = target
        self.refdb = refdb
        self.refid = refid
        # "human-readable" text of referenced ID (optional)
        self.reftext = tail.lstrip('\t').rstrip('\n')

    def __str__(self):
        return u'%s\t%s %s %s:%s%s' % (
            self.id,
            self.type,
            self.target,
            self.refdb,
            self.refid,
            self.tail,
        )

    def get_deps(self):
        soft_deps, hard_deps = IdedAnnotation.get_deps(self)
        hard_deps.add(self.target)
        return (soft_deps, hard_deps)

    def reference_id(self):
        # TODO: can't currently ID normalization in isolation; return
        # reference to target instead
        return [self.target]

    @classmethod
    def from_list(cls, list, annotations):
        return NormalizationAnnotation(list[0], list[1], list[2], list[3], list[4], u'\t'+list[5])

    def to_list(self):
        return [self.id, self.type, self.target, self.refdb, self.refid, self.reftext]


class OnelineCommentAnnotation(IdedAnnotation):
    def __init__(self, target, id, type, tail, source_id=None):
        IdedAnnotation.__init__(self, id, type, tail, source_id=source_id)
        self.target = target

    def __str__(self):
        return u'%s\t%s %s%s' % (
            self.id,
            self.type,
            self.target,
            self.tail
        )

    def get_text(self):
        # TODO: will this always hold? Wouldn't it be better to parse
        # further rather than just assuming the whole tail is the text?
        return self.tail.strip()

    def get_deps(self):
        soft_deps, hard_deps = IdedAnnotation.get_deps(self)
        hard_deps.add(self.target)
        return (soft_deps, hard_deps)

    @classmethod
    def from_list(cls, list, annotations):
        return OnelineCommentAnnotation(list[0], annotations.get_new_id('#'), list[1], list[2])

    def to_list(self):
        return [self.target, self.type, self.tail]


class TextBoundAnnotation(IdedAnnotation):
    """
    Represents a text-bound annotation. Text-bound annotations
    identify a specific span of text and assign it a type.  This base
    class does not assume ability to access text; use
    TextBoundAnnotationWithText for that.

    Represented in standoff as

    ID\tTYPE START END

    Where START and END are positive integer offsets identifying the
    span of the annotation in text. Discontinuous annotations can be
    represented as

    ID\tTYPE START1 END1;START2 END2;...

    with multiple START END pairs separated by semicolons.
    """

    def __init__(self, spans, id, type, tail, source_id=None):
        # Note: if present, the text goes into tail
        IdedAnnotation.__init__(self, id, type, tail, source_id=source_id)
        self.spans = spans
        self.check_spans()

    def check_spans(self):
        for i in range(0, len(self.spans)):
            if isinstance(self.spans[i], list):
                self.spans[i] = (self.spans[i][0], self.spans[i][1])

    # TODO: temp hack while building support for discontinuous
    # annotations; remove once done
    def get_start(self):
        Messager.warning('TextBoundAnnotation.start access')
        return self.spans[0][0]

    def get_end(self):
        Messager.warning('TextBoundAnnotation.end access')
        return self.spans[-1][1]

    start = property(get_start)
    end = property(get_end)

    # end hack

    def first_start(self):
        """
        Return the first (min) start offset in the annotation spans.
        """
        return min([start for start, end in self.spans])

    def last_end(self):
        """
        Return the last (max) end offset in the annotation spans.
        """
        return max([end for start, end in self.spans])

    def get_text(self):
        # If you're seeing this exception, you probably need a
        # TextBoundAnnotationWithText. The underlying issue may be
        # that you're creating an Annotations object instead of
        # TextAnnotations.
        raise NotImplementedError

    def same_span(self, other):
        """
        Determine if a given other TextBoundAnnotation has the same
        span as this one. Returns True if each (start, end) span of
        the other annotation is equivalent with at least one span of
        this annotation, False otherwise.
        """
        return set(self.spans) == set(other.spans)

    def contains(self, other):
        """
        Determine if a given other TextBoundAnnotation is contained in
        this one. Returns True if each (start, end) span of the other
        annotation is inside (or equivalent with) at least one span
        of this annotation, False otherwise.
        """
        for o_start, o_end in other.spans:
            contained = False
            for s_start, s_end in self.spans:
                if o_start >= s_start and o_end <= s_end:
                    contained = True
                    break
            if not contained:
                return False
        return True

    def __str__(self):
        return u'%s\t%s %s%s' % (
            self.id,
            self.type,
            ';'.join(['%d %d' % (start, end) for start, end in self.spans]),
            self.tail
        )

    @classmethod
    def from_list(cls, list, annotations):
        ann_text = DISCONT_SEP.join((annotations._document.text[start:end]
                                     for start, end in list[2]))
        return TextBoundAnnotation(list[2], list[0], list[1], ann_text)

    def to_list(self):
        return [self.id, self.type, self.spans]


class TextBoundAnnotationWithText(TextBoundAnnotation):
    """
    Represents a text-bound annotation. Text-bound annotations
    identify a specific span of text and assign it a type.  This class
    assume that the referenced text is included in the annotation.

    Represented in standoff as

    ID\tTYPE START END\tTEXT

    Where START and END are positive integer offsets identifying the
    span of the annotation in text and TEXT is the corresponding text.
    Discontinuous annotations can be represented as

    ID\tTYPE START1 END1;START2 END2;...

    with multiple START END pairs separated by semicolons.
    """

    def __init__(self, spans, id, type, text, text_tail="", source_id=None):
        IdedAnnotation.__init__(self, id, type, '\t' + text + text_tail, source_id=source_id)
        self.spans = spans
        self.text = text
        self.text_tail = text_tail
        self.check_spans()

    # TODO: temp hack while building support for discontinuous
    # annotations; remove once done
    def get_start(self):
        Messager.warning('TextBoundAnnotationWithText.start access')
        return self.spans[0][0]

    def get_end(self):
        Messager.warning('TextBoundAnnotationWithText.end access')
        return self.spans[-1][1]

    start = property(get_start)
    end = property(get_end)

    # end hack

    def get_text(self):
        return self.text

    def __str__(self):
        # log_info('TextBoundAnnotationWithText: __str__: "%s"' % self.text)
        return u'%s\t%s %s\t%s%s' % (
            self.id,
            self.type,
            ';'.join(['%d %d' % (start, end) for start, end in self.spans]),
            self.text,
            self.text_tail
        )

    @classmethod
    def from_list(cls, list, annotations):
        ann_text = DISCONT_SEP.join((annotations._document.text[start:end]
                                     for start, end in list[2]))
        return TextBoundAnnotationWithText(list[2], list[0], list[1], ann_text)


class BinaryRelationAnnotation(IdedAnnotation):
    """
    Represents a typed binary relation annotation. Relations are
    assumed not to be symmetric (i.e are "directed"); for equivalence
    relations, EquivAnnotation is likely to be more appropriate.
    Unlike events, relations are not associated with text expressions
    (triggers) stating them.

    Represented in standoff as

    ID\tTYPE ARG1:ID1 ARG2:ID2

    Where ARG1 and ARG2 are arbitrary (but not identical) labels.
    """

    def __init__(self, id, type, arg1l, arg1, arg2l, arg2, tail, source_id=None):
        IdedAnnotation.__init__(self, id, type, tail, source_id=source_id)
        self.arg1l = arg1l
        self.arg1 = arg1
        self.arg2l = arg2l
        self.arg2 = arg2

    def __str__(self):
        return u'%s\t%s %s:%s %s:%s%s' % (
            self.id,
            self.type,
            self.arg1l,
            self.arg1,
            self.arg2l,
            self.arg2,
            self.tail
        )

    def get_deps(self):
        soft_deps, hard_deps = IdedAnnotation.get_deps(self)
        hard_deps.add(self.arg1)
        hard_deps.add(self.arg2)
        return soft_deps, hard_deps

    @classmethod
    def from_list(cls, list, annotations):
        return BinaryRelationAnnotation(list[0], list[1], list[2][0][0], list[2][0][1], list[2][1][0], list[2][1][1], '\t')

    def to_list(self):
        return [self.id, self.type, [(self.arg1l, self.arg1), (self.arg2l, self.arg2)]]
