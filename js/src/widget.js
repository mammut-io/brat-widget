var widgets = require('jupyter-js-widgets');
var _ = require('underscore');
var $ = require('jquery');

// brat jquery-theme styles
require('./static/jquery-theme/jquery-ui.css');
require('./static/jquery-theme/jquery-ui-redmond.css');
// brat styles
require('./static/style-vis.css');
require('./static/style-ui.css');
require('./static/style.css');
//brat images
var spinnerGif = require('./static/img/spinner.gif');
var fugueShadowlessMagnifierPng = require('./static/img/Fugue-shadowless-magnifier.png');
var fugueShadowlessExternalPng = require('./static/img/Fugue-shadowless-external.png');
//brat fonts
var webFontURLs = [
    require('file-loader!./static/fonts/Astloch-Bold.ttf'),
    require('file-loader!./static/fonts/PT_Sans-Caption-Web-Regular.ttf'),
    require('file-loader!./static/fonts/Liberation_Sans-Regular.ttf')
];
//brat modules
var Dispatcher = require('./dispatcher');
var Visualizer = require('./visualizer');
var VisualizerUI = require('./visualizer_ui');
var URLMonitor = require('./url_monitor').URLMonitor;
var Ajax = require('./ajax');
var AnnotatorUI = require('./annotator_ui');
var Spinner = require('./spinner')
var AnnotationLog = require('./annotation_log');


// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var VisualizerModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
        _model_name: 'VisualizerModel',
        _view_name: 'VisualizerView',
        _model_module: 'brat-widget',
        _view_module: 'brat-widget',
        _model_module_version: '0.1.0',
        _view_module_version: '0.1.0',
        collection: {},
        value: {}
    })
});


var AnnotatorModel = VisualizerModel.extend({
    defaults: _.extend(_.result(this, 'widgets.DOMWidgetModel.prototype.defaults'), {
        _model_name: 'AnnotatorModel',
        _view_name: 'AnnotatorView'
    })
});


// Custom View. Renders the widget model.
var VisualizerView = widgets.DOMWidgetView.extend({
    render: function () {
        console.log('Value changed!!!');
        this.value_changed();
        if (this.dispatcher === undefined) {
            this.el.id = "brat_" + new Date().getTime().toString();
            var $divSvg = $("<div id='" + this.el.id + "_svg'></div>").appendTo(this.el);
            this.embed($divSvg, this.model.get('collection'), this.model.get('value'));
        }
        this.model.on('change:value', this.value_changed, this);
    },

    value_changed: function () {
        console.log('Value changed!!!');
    },

    // container: ID or jQuery element
    // collData: the collection data (in the format of the result of
    //   http://.../brat/ajax.cgi?action=getCollectionInformation&collection=...
    // docData: the document data (in the format of the result of
    //   http://.../brat/ajax.cgi?action=getDocument&collection=...&document=...
    // returns the embedded visualizer's dispatcher object
    embed: function (container, collData, docData) {
        if (this.dispatcher === undefined) {
            this.dispatcher = new Dispatcher();
        }
        if (this.visualizer === undefined) {
            this.visualizer = new Visualizer(this.el.id, this.dispatcher, container, webFontURLs);
        }
        docData.collection = null;
        this.dispatcher.post('collectionLoaded', [collData]);
        this.dispatcher.post('requestRenderData', [docData]);
    }
});


var VisualizerUIsimulator = (function ($, window, undefined) {
    var VisualizerUIsimulator = function (base_id, dispatcher, svg) {
        /* START message display - related */
        var $pulluptrigger = $('#' + base_id + '_pulluptrigger');
        var showPullupTrigger = function () {
            $pulluptrigger.show('puff');
        };
        var $messageContainer = $('#' + base_id + '_messages');
        var $messagepullup = $('#' + base_id + '_messagepullup');
        var pullupTimer = null;
        var displayMessages = function (msgs) {
            var initialMessageNum = $messagepullup.children().length;

            if (msgs === false) {
                console.log('Simulator - Messages: clean all messages.');
                $messageContainer.children().each(function (msgElNo, msgEl) {
                    $(msgEl).remove();
                });
            } else {
                $.each(msgs, function (msgNo, msg) {
                    console.log('Simulator - Messages: ' + msg);
                    var element;
                    var timer = null;
                    try {
                        element = $('<div class="' + msg[1] + '">' + msg[0] + '</div>');
                    }
                    catch (x) {
                        escaped = msg[0].replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                        element = $('<div class="error"><b>[ERROR: could not display the following message normally due to malformed XML:]</b><br/>' + escaped + '</div>');
                    }
                    var pullupElement = element.clone();
                    $messageContainer.append(element);
                    $messagepullup.append(pullupElement.css('display', 'none'));
                    slideToggle(pullupElement, true, true);

                    var fader = function () {
                        if ($messagepullup.is(':visible')) {
                            element.remove();
                        } else {
                            element.hide('slow', function () {
                                element.remove();
                            });
                        }
                    };
                    var delay = (msg[2] === undefined)
                        ? messageDefaultFadeDelay
                        : (msg[2] === -1)
                            ? null
                            : (msg[2] * 1000);
                    if (delay === null) {
                        var button = $('<input type="button" value="OK"/>');
                        element.prepend(button);
                        button.click(function (evt) {
                            timer = setTimeout(fader, 0);
                        });
                    } else {
                        timer = setTimeout(fader, delay);
                        element.mouseover(function () {
                            clearTimeout(timer);
                            element.show();
                        }).mouseout(function () {
                            timer = setTimeout(fader, messagePostOutFadeDelay);
                        });
                    }
                    // setTimeout(fader, messageDefaultFadeDelay);
                });

                // limited history - delete oldest
                var $messages = $messagepullup.children();
                for (var i = 0; i < $messages.length - maxMessages; i++) {
                    $($messages[i]).remove();
                }
            }

            // if there is change in the number of messages, may need to
            // tweak trigger visibility
            var messageNum = $messagepullup.children().length;
            if (messageNum != initialMessageNum) {
                if (messageNum == 0) {
                    // all gone; nothing to trigger
                    $('#' + base_id + '_pulluptrigger').hide('slow');
                } else if (initialMessageNum == 0) {
                    // first messages, show trigger at fade
                    setTimeout(showPullupTrigger, messageDefaultFadeDelay + 250);
                }
            }
        };
        // hide pullup trigger by default, show on first message
        $pulluptrigger.hide();
        $pulluptrigger.mouseenter(function (evt) {
            $('#' + base_id + '_pulluptrigger').hide('puff');
            clearTimeout(pullupTimer);
            slideToggle($messagepullup.stop(), true, true, true);
        });
        $messagepullup.mouseleave(function (evt) {
            setTimeout(showPullupTrigger, 500);
            clearTimeout(pullupTimer);
            pullupTimer = setTimeout(function () {
                slideToggle($messagepullup.stop(), false, true, true);
            }, 500);
        });
        /* END message display - related */

        /* START form management - related */
        var initForm = function (form, opts) {
            opts = opts || {};
            //var formId = form.attr('id');

            // alsoResize is special
            var alsoResize = opts.alsoResize;
            delete opts.alsoResize;

            // Always add OK and Cancel
            var buttons = (opts.buttons || []);
            if (opts.no_ok) {
                delete opts.no_ok;
            } else {
                buttons.push({
                    //id: formId + "-ok",
                    text: "OK",
                    click: function () {
                        //form.submit();
                    }
                });
            }
            if (opts.no_cancel) {
                delete opts.no_cancel;
            } else {
                buttons.push({
                    //id: formId + "-cancel",
                    text: "Cancel",
                    click: function () {
                        form.dialog('close');
                    }
                });
            }
            delete opts.buttons;

            opts = $.extend({
                autoOpen: false,
                closeOnEscape: true,
                buttons: buttons,
                modal: true
            }, opts);

            //form.dialog(opts);
            //form.bind('dialogclose', function () {
            //    if (form == currentForm) {
            //        currentForm = null;
            //    }
            //});

            // HACK: jQuery UI's dialog does not support alsoResize
            // nor does resizable support a jQuery object of several
            // elements
            // See: http://bugs.jqueryui.com/ticket/4666
            if (alsoResize) {
                //form.parent().resizable('option', 'alsoResize',
                //    '#' + form.attr('id') + ', ' + alsoResize);
            }
        };

        var unsafeDialogOpen = function ($dialog) {
            // does not restrict tab key to the dialog
            // does not set the focus, nor change position
            // but is much faster than dialog('open') for large dialogs, see
            // https://github.com/nlplab/brat/issues/934

            var self = $dialog.dialog('instance');

            if (self._isOpen) {
                return;
            }

            self._isOpen = true;
            self.opener = $(self.document[0].activeElement);

            self._size();
            self._createOverlay();
            self._moveToTop(null, true);

            if (self.overlay) {
                self.overlay.css("z-index", self.uiDialog.css("z-index") - 1);
            }
            self._show(self.uiDialog, self.options.show);
            self._trigger('open');
        };

        var showForm = function (form, unsafe) {
            currentForm = form;
            // as suggested in http://stackoverflow.com/questions/2657076/jquery-ui-dialog-fixed-positioning
            form.parent().css({position: "fixed"});
            if (unsafe) {
                unsafeDialogOpen(form);
            } else {
                form.dialog('open');
            }
            slideToggle($('#pulldown').stop(), false);
            return form;
        };

        var hideForm = function () {
            if (!currentForm) return;
            // currentForm.fadeOut(function() { currentForm = null; });
            currentForm.dialog('close');
            currentForm = null;
        };

        /* END form management - related */

        dispatcher.on('messages', displayMessages).on('initForm', initForm);
        return {
            initForm: initForm
        };
    };

    return VisualizerUIsimulator;
})($, window);


var AnnotatorView = VisualizerView.extend({
        set_ajax_simulator: function (dispatcher) {
            var PROTOCOL_VERSION = 1;
            var pending = 0;
            var count = 0;
            var pendingList = {};

            // merge data will get merged into the response data
            // before calling the callback
            var ajaxCall = function (data, callback, merge, extraOptions) {
                merge = merge || {};
                dispatcher.post('spin');
                pending++;
                var id = count++;

                // special value: `merge.keep = true` prevents obsolescence
                pendingList[id] = merge.keep || false;
                delete merge.keep;

                // If no protocol version is explicitly set, set it to current
                if (data.toString() == '[object FormData]') {
                    data.append('protocol', PROTOCOL_VERSION);
                } else if (data['protocol'] === undefined) {
                    // TODO: Extract the protocol version somewhere global
                    data['protocol'] = PROTOCOL_VERSION;
                }

                options = {
                    url: 'ajax.cgi',
                    data: data,
                    type: 'POST',
                    success: function (response) {
                        pending--;
                        // If no exception is set, verify the server results
                        if (response.exception == undefined && response.action !== data.action) {
                            console.error('Action ' + data.action +
                                ' returned the results of action ' + response.action);
                            response.exception = true;
                            dispatcher.post('messages', [[['Protocol error: Action' + data.action + ' returned the results of action ' + response.action + ' maybe the server is unable to run, please run tools/troubleshooting.sh from your installation to diagnose it', 'error', -1]]]);
                        }

                        // If the request is obsolete, do nothing; if not...
                        if (pendingList.hasOwnProperty(id)) {
                            dispatcher.post('messages', [response.messages]);
                            if (response.exception == 'configurationError'
                                || response.exception == 'protocolVersionMismatch') {
                                // this is a no-rescue critical failure.
                                // Stop *everything*.
                                pendingList = {};
                                dispatcher.post('screamingHalt');
                                // If we had a protocol mismatch, prompt the user for a reload
                                if (response.exception == 'protocolVersionMismatch') {
                                    if (confirm('The server is running a different version ' +
                                            'from brat than your client, possibly due to a ' +
                                            'server upgrade. Would you like to reload the ' +
                                            'current page to update your client to the latest ' +
                                            'version?')) {
                                        window.location.reload(true);
                                    } else {
                                        dispatcher.post('messages', [[['Fatal Error: Protocol ' +
                                        'version mismatch, please contact the administrator',
                                            'error', -1]]]);
                                    }
                                }
                                return;
                            }

                            delete pendingList[id];

                            // if .exception is just Boolean true, do not process
                            // the callback; if it is anything else, the
                            // callback is responsible for handling it
                            if (response.exception == true) {
                                $('#waiter').dialog('close');
                            } else if (callback) {
                                $.extend(response, merge);
                                dispatcher.post(0, callback, [response]);
                            }
                        }
                        dispatcher.post('unspin');
                    },
                    error: function (response, textStatus, errorThrown) {
                        pending--;
                        dispatcher.post('unspin');
                        $('#waiter').dialog('close');
                        dispatcher.post('messages', [[['Error: Action' + data.action + ' failed on error ' + response.statusText, 'error']]]);
                        console.error(textStatus + ':', errorThrown, response);
                    }
                };

                if (extraOptions) {
                    $.extend(options, extraOptions);
                }
                $.ajax(options);
                return id;
            };

            var isReloadOkay = function () {
                // do not reload while data is pending
                return pending == 0;
            };

            var makeObsolete = function (all) {
                if (all) {
                    pendingList = {};
                } else {
                    $.each(pendingList, function (id, keep) {
                        if (!keep) delete pendingList[id];
                    });
                }
            };

            dispatcher.on('isReloadOkay', isReloadOkay).on('makeAjaxObsolete', makeObsolete).on('ajax', ajaxCall);
        },

        render: function () {
            AnnotatorView.__super__.render.apply(this);
        },

        embed: function (container, collData, docData) {
            AnnotatorView.__super__.embed.apply(this, arguments);
            if (this.urlMonitor === undefined) {
                $(this.get_forms_div_str()).appendTo(this.el);
                $(this.get_messages_div_str()).appendTo(this.el);

                this.urlMonitor = new URLMonitor(this.el.id, this.dispatcher);
                //this.set_ajax_simulator(this.dispatcher);
                this.ajax = new Ajax(this.el.id, this.dispatcher);
                //this.visualizerUI = new VisualizerUIsimulator(this.el.id, this.dispatcher, this.visualizer.svg);
                this.visualizerUI = new VisualizerUI(this.el.id, this.dispatcher, this.visualizer.svg);
                this.annotatorUI = new AnnotatorUI(this.el.id, this.dispatcher, this.visualizer.svg, this.visualizerUI.initForm);
                this.spinner = new Spinner(this.dispatcher, '#' + this.el.id + '_spinner');
                //this.logger = new AnnotationLog(this.dispatcher);
                this.dispatcher.post('init');
            }
        },

        get_interpolat_dom: function (str_to_interpolate) {
            var o = {base_id: this.el.id};
            return str_to_interpolate.replace(/{([^{}]*)}/g,
                function (a, b) {
                    var r = o[b];
                    return typeof r === 'string' || typeof r === 'number' ? r : a;
                }
            );
        },

        get_forms_div_str: function () {
            var strForms = `<div id='{base_id}_forms'><form id="{base_id}_import_form" class="dialog" title="Import">
      <fieldset id="import_form_docid">
        <legend>Document ID</legend>
        <input id="import_docid" class="borderless"/>
      </fieldset>
      <fieldset id="import_form_text">
        <legend>Document text</legend>
        <textarea id="import_text" class="borderless"/>
      </fieldset>
    </form>
    <form id="{base_id}_import_coll_form" class="dialog" title="Import collection">
      <fieldset id="import_coll_form_text">
        <legend>Collection archive (.zip, .tar.gz)</legend>
        <input type="file" id="import_coll" class="borderless" accept="application/zip,application/x-gzip" />
      </fieldset>
    </form>
    <!-- Data dialog -->
    <form id="{base_id}_data_form" class="dialog" title="Data">
      <!-- Data dialog export section -->
      <fieldset class="small-buttons">
        <legend>Export</legend>
        <div class="optionRow">
          <span id="document_export" class="optionLabel">Document data</span>
          <span id="source_files"/>
        </div>
        <div id="document_visualization" class="optionRow">
          <span class="optionLabel">Visualization</span>
          <span id="stored_file_spinner" class="ui-button ui-widget ui-corner-all ui-state-default ui-button-text-only">
            <span class="ui-button-text">
              <img style="vertical-align:bottom" height="18"
                   src="` + spinnerGif + `"/>
            </span>
          </span>
          <span id="stored_file_regenerate" title="Regenerate static visualization of the current document">regenerate</span>
          <span id="download_stored"/>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Collection data</span>
          <span id="source_collection" title="Download the entire current collection as a .tar.gz package"/>
          Conf files:
          <span id="source_collection_conf">
            <input type="radio" id="source_collection_conf_off" value="0"
                   name="source_collection_conf_radio"/>
            <label for="source_collection_conf_off"
                   title="Do not include the configuration files">off</label>
            <input type="radio" id="source_collection_conf_on" value="1"
                   name="source_collection_conf_radio" checked="checked"/>
            <label for="source_collection_conf_on"
                   title="Do include the configuration files">on</label>
          </span>
        </div>
      </fieldset>
      <!-- Data dialog comparison section -->
      <fieldset class="small-buttons">
        <legend>Compare</legend>
        <div class="optionRow">
          <span class="optionLabel">Side-by-side</span>
          <span id="side-by-side_cmp" title="Enter side-by-side comparison mode"/>
        </div>
      </fieldset>
      <!-- Data dialog automatic annotation section -->
      <div id="auto_tagging_login_control" class="login">
        <fieldset id="auto_tagging_fieldset" class="small-buttons">
          <legend>Automatic annotation</legend>
          <div class="optionRow">Automatically tag current document</div>
          <div id="tagger_buttons"/>
        </fieldset>
        <fieldset id="no_tagger_message" style="display:none">
          <legend>Automatic annotation</legend>
          <div style="color:gray; font-size:80%; text-align:center; margin:1em">(No tools set up. Please contact server administrator if needed.)</div>
        </fieldset>
      </div>
      <!-- Data dialog import section -->
      <fieldset class="login small-buttons">
        <legend>Import</legend>
        <div class="optionRow">
          <span class="optionLabel">New document</span>
          <input id="import_button" type="button" class="login ui-button-text" value="Enter text" tabindex="-1" title="Import a new document into the current collection"/>
        </div>
        <!-- XXX Taken out until such time when serverside is
                 implemented, pending resolution of issues
                 raised in #216
        <div class="optionRow">
          <span class="optionLabel">New collection</span>
          <input id="import_collection_button" type="button" class="login ui-button-text" value="Upload archive" tabindex="-1" title="Import an entire collection into the current installation"/>
        </div>
        -->
      </fieldset>
      <!-- Data dialog delete section -->
      <div style="display: none;">
        <fieldset class="login small-buttons">
          <legend>Delete</legend>
          <div class="optionRow">
            <span class="optionLabel">Current document</span>
            <input id="delete_document_button" type="button" class="login ui-button-text" value="Delete document" tabindex="-1" title="Permanently remove the current document and its annotations from the collection."/>
          </div>
          <div class="optionRow">
            <span class="optionLabel">Current collection</span>
            <input id="delete_collection_button" type="button" class="login ui-button-text" value="Delete collection" tabindex="-1" title="Permanently remove the entire current collection and all documents in it."/>
          </div>
        </fieldset>
      </div>
    </form>
    <!-- Options dialog -->
    <form id="{base_id}_options_form" class="dialog" title="Options">
      <fieldset id="options_form_visual">
        <legend>Visual options</legend>
        <div class="optionRow">
          <span class="optionLabel">Abbreviate labels</span>
          <span id="label_abbreviations" class="radio_group small-buttons">
            <input type="radio" id="label_abbreviations_off" value="off"
                   name="label_abbrev_radio"/>
            <label for="label_abbreviations_off"
                   title="Always display full form of labels.">Off</label>
            <input type="radio" id="label_abbreviations_on" value="on"
                   name="label_abbrev_radio" checked="checked"/>
            <label for="label_abbreviations_on"
                   title="Abbreviate annotation labels in limited space.">On</label>
          </span>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Text background</span>
          <span id="text_backgrounds" class="radio_group small-buttons">
            <input type="radio" id="text_backgrounds_blank" value="blank"
                   name="text_background_radio"/>
            <label for="text_backgrounds_blank"
                   title="Blank white text backgrounds.">Blank</label>
            <input type="radio" id="text_backgrounds_striped" value="striped"
                   name="text_background_radio" checked="checked"/>
            <label for="text_backgrounds_striped"
                   title="Striped text backgrounds with every second sentence on light gray background.">Striped</label>
          </span>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Layout density</span>
          <span id="layout_density" class="radio_group small-buttons">
            <input type="radio" id="layout_density1" value="1"
                   name="layout_radio"/>
            <label for="layout_density1"
                   title="Dense annotation layout: minimizes space taken by annotations.">Dense</label>
            <input type="radio" id="layout_density2" value="2"
                   name="layout_radio" checked="checked" />
            <label for="layout_density2"
                   title="Normal annotation layout density: balances between annotation size and readability.">Normal</label>
            <input type="radio" id="layout_density3" value="3"
                   name="layout_radio"/>
            <label for="layout_density3"
                   title="Spacious annotation layout: allows extra space for annotations to improve readability.">Spacious</label>
          </span>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Visualization width</span>
          <input id="svg_width_value" maxlength="3" size="3" value="100"
                 style="text-align:right"/>
          <span id="svg_width_unit" class="radio_group small-buttons">
            <input type="radio" id="svg_width_unit_percent" value="%"
                   name="svg_width_radio" checked="checked"/>
            <label for="svg_width_unit_percent">percent</label>
            <input type="radio" id="svg_width_unit_pixels" value="px"
                   name="svg_width_radio"/>
            <label for="svg_width_unit_pixels">pixels</label>
          </span>
        </div>
      </fieldset>
      <fieldset id="options_form_annotation" class="login">
        <legend>Annotation options</legend>
        <div class="optionRow">
          <span class="optionLabel">Annotation mode</span>
          <span id="annotation_speed" class="radio_group small-buttons">
            <input type="radio" id="annotation_speed1" value="1"
                   name="annspeed_radio" checked="checked"/>
            <label for="annotation_speed1"
                   title="Careful annotation mode: ask for additional confirmation of annotation changes. Suitable for annotators in training and for mature corpora requiring few changes.">Careful</label>
            <input type="radio" id="annotation_speed2" value="2"
                   name="annspeed_radio"/>
            <label for="annotation_speed2"
                   title="Normal annotation mode. Suitable for standard annotation processes.">Normal</label>
            <input type="radio" id="annotation_speed3" value="3"
                   name="annspeed_radio"/>
            <label for="annotation_speed3"
                   title="Rapid annotation mode: activate automatic support for speeding up annotation process. Suitable for experienced annotators performing an established task.">Rapid</label>
            <select id="rapid_model"/>
          </span>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Type Collapse Limit</span>
          <input id="type_collapse_limit" maxlength="3" size="3" value="30"
                 style="text-align:right"/>
        </div>
      </fieldset>
      <fieldset id="options_form_network">
        <legend>Network options</legend>
        <div class="optionRow">
          <span class="optionLabel">Collaboration</span>
          <span class="small-buttons">
            <input id="autorefresh_mode" type="checkbox"/>
            <label for="autorefresh_mode"
                   title="Toggle the autorefresh mode on/off. When autorefresh is on, the system will periodically check with the server for updates to the document you are working on. This is useful when collaborating on annotation but consumes some resources, so you may wish to turn autorefresh off if there are no simultaneous edits.">Autorefresh</label>
          </span>
        </div>
      </fieldset>
    </form>
    <!-- More collection information dialog -->
    <form id="{base_id}_more_information_dialog" class="dialog" title="Collection information">
      <fieldset>
        <textarea id="more_info_readme" readonly="readonly" class="borderless"/>
      </fieldset>
    </form>
    <!-- Search dialog -->
    <form id="{base_id}_search_form" class="dialog" title="Search">
      <div id="search_tabs">
        <ul>
          <li><a href="#search_tab_text">Text</a></li>
          <li><a href="#search_tab_entity">Entity</a></li>
          <li><a href="#search_tab_event">Event</a></li>
          <li><a href="#search_tab_relation">Relation</a></li>
          <li><a href="#search_tab_note">Note</a></li>
          <!-- XXX removed per #900
          <li><a href="#search_tab_load">Load</a></li>
          -->
        </ul>
        <div id="search_tab_text">
          <table class="fullwidth">
            <tr>
              <td>Text</td>
              <td>
                <input id="search_form_text_text" class="fullwidth"
                    placeholder="Text to match"/>
              </td>
            </tr>
          </table>
        </div>
        <div id="search_tab_entity">
          <table class="fullwidth">
            <tr>
              <td>Type</td>
              <td>
                <select id="search_form_entity_type"/>
              </td>
            </tr>
            <tr>
              <td>Text</td>
              <td>
                <input id="search_form_entity_text" class="fullwidth"
                    placeholder="Text to match (empty=anything)"/>
              </td>
            </tr>
          </table>
        </div>
        <div id="search_tab_event">
          <table class="fullwidth">
            <tr>
              <td>Type</td>
              <td colspan="3">
                <select id="search_form_event_type"/>
              </td>
            </tr>
            <tr>
              <td>Trigger</td>
              <td colspan="3">
                <input id="search_form_event_trigger" class="fullwidth"
                    placeholder="Text to match (empty=anything)"/>
              </td>
            </tr>
            <tbody id="search_form_event_roles"/>
          </table>
        </div>
        <div id="search_tab_relation">
          <table class="fullwidth">
            <tr>
              <td>Type</td>
              <td colspan="2">
                <select id="search_form_relation_type" class="fullwidth"/>
              </td>
            </tr>
            <tr>
              <td>Arg1</td>
              <td>
                <select id="search_form_relation_arg1_type" class="fullwidth"/>
              </td>
              <td>
                <input id="search_form_relation_arg1_text" class="fullwidth"
                    placeholder="Text to match (empty=anything)"/>
              </td>
            </tr>
            <tr>
              <td>Arg2</td>
              <td>
               <select id="search_form_relation_arg2_type" class="fullwidth"/>
              </td>
              <td>
                <input id="search_form_relation_arg2_text" class="fullwidth"
                    placeholder="Text to match (empty=anything)"/>
              </td>
            </tr>
          </table>
          <div class="optionRow">
            <span class="optionLabel">Show arg text</span>
            <span id="search_form_relation_show_arg_text"
                  class="radio_group small-buttons">
              <input type="radio" id="search_form_relation_show_arg_text_off"
                     value="off" name="search_form_relation_show_arg_text_radio"
                     checked="checked"/>
              <label for="search_form_relation_show_arg_text_off"
                     title="Don't show texts of relation arguments in search results.">off</label>
              <input type="radio" id="search_form_relation_show_arg_text_on"
                     value="on"
                     name="search_form_relation_show_arg_text_radio"/>
              <label for="search_form_relation_show_arg_text_on"
                     title="Show texts of relation arguments in search results.">on</label>
            </span>
          </div>
          <div class="optionRow">
            <span class="optionLabel">Show arg type</span>
            <span id="search_form_relation_show_arg_type"
                  class="radio_group small-buttons">
              <input type="radio" id="search_form_relation_show_arg_type_off"
                     value="off" name="search_form_relation_show_arg_type_radio"
                     checked="checked"/>
              <label for="search_form_relation_show_arg_type_off"
                     title="Don't show types of relation arguments in search results.">off</label>
              <input type="radio" id="search_form_relation_show_arg_type_on"
                     value="on"
                     name="search_form_relation_show_arg_type_radio"/>
              <label for="search_form_relation_show_arg_type_on"
                     title="Show types of relation arguments in search results.">on</label>
            </span>
          </div>
        </div>
        <div id="search_tab_note">
          <table class="fullwidth">
            <tr>
              <td>Category</td>
              <td>
                <select id="search_form_note_category" class="fullwidth">
                  <option value="">- Any -</option>
                  <option value="entity">Entity</option>
                  <option value="event">Event</option>
                  <option value="relation">Relation</option>
                  <option value="sentence">Sentence</option>
                </select>
              </td>
            </tr>
            <tr id="search_form_note_type_row">
              <td>Type</td>
              <td>
                <select id="search_form_note_type" class="fullwidth"/>
              </td>
            </tr>
            <tr>
              <td>Text</td>
              <td>
                <input id="search_form_note_text" class="fullwidth"
                    placeholder="Text to match (empty=anything)"/>
              </td>
            </tr>
          </table>
        </div>
        <!-- XXX removed per #900
        <div id="search_tab_load">
          <table class="fullwidth">
            <tr>
              <td>File:</td>
              <td>
                <input type="file" name="file" id="search_form_load_file" class="fullwidth"/>
                <input type="hidden" name="action" value="searchLoad"/>
              </td>
            </tr>
          </table>
        </div>
        -->
      </div>
      <fieldset id="search_options">
        <legend>Options</legend>
        <a href="" id="advanced_search_option_toggle">Show advanced</a>
        <div class="optionRow">
          <span class="optionLabel">Search in current</span>
          <span id="search_scope" class="radio_group small-buttons">
            <input type="radio" id="search_scope_doc" value="document"
                   name="search_scope_radio" checked="checked"/>
            <label for="search_scope_doc"
                   title="Search in current document only.">document</label>
            <input type="radio" id="search_scope_coll" value="collection"
                   name="search_scope_radio"/>
            <label for="search_scope_coll"
                   title="Search in all documents in current collection.">collection</label>
          </span>
        </div>
        <div class="advancedOptions">
        <div class="optionRow">
          <span class="optionLabel">Concordancing</span>
          <span id="concordancing" class="radio_group small-buttons">
            <input type="radio" id="concordancing_off" value="document"
                   name="concordancing_radio" checked="checked"/>
            <label for="concordancing_off"
                   title="Display matched search results only.">off</label>
            <input type="radio" id="concordancing_on" value="collection"
                   name="concordancing_radio"/>
            <label for="concordancing_on"
                   title="In addition to search results, display also the text context of the matches in Key Word In Context (KWIC) format.">on</label>
          </span>
        </div>
        <div id="context_size_div" class="optionRow">
          <span class="optionLabel" style="margin-left:1em;">Context length</span> <input id="context_length" maxlength="3" size="3" value="50"/> characters
        </div>
        <div class="optionRow">
          <span class="optionLabel">Match text as</span>
          <span id="text_match" class="radio_group small-buttons">
            <input type="radio" id="text_match_word" value="word"
                   name="text_match_radio" checked="checked"/>
            <label for="text_match_word"
                   title="Match whole words only.">whole word</label>
            <input type="radio" id="text_match_substr" value="substring"
                   name="text_match_radio"/>
            <label for="text_match_substr"
                   title="Match any substring.">any substring</label>
            <input type="radio" id="text_match_regex" value="regex"
                   name="text_match_radio"/>
            <label for="text_match_regex"
                   title="Treat given text as regular expression.">regex</label>
          </span>
        </div>
        <div class="optionRow">
          <span class="optionLabel">Match case</span>
          <span id="match_case" class="radio_group small-buttons">
            <input type="radio" id="match_case_off" value="document"
                   name="match_case_radio" checked="checked"/>
            <label for="match_case_off"
                   title="Ignore character case in text search ('abc' matches 'ABC')">off</label>
            <input type="radio" id="match_case_on" value="collection"
                   name="match_case_radio"/>
            <label for="match_case_on"
                   title="Require identical character case in text search ('abc' does not match 'ABC')">on</label>
          </span>
        </div>
        </div>
      </fieldset>
    </form>
    <!-- Span dialog (view only) -->
    <form id="{base_id}_viewspan_form" class="dialog" title="Span">
      <fieldset id="viewspan_selected_fset">
        <legend>Text</legend>
        <a target="brat_linked" id="viewspan_highlight_link" href="#">Link</a>
        <div id="viewspan_selected"/>
      </fieldset>

      <fieldset id="viewspan_search_fieldset">
        <legend>Search</legend>
        <div id="viewspan_search_links"/>
      </fieldset>

      <fieldset>
        <legend>Notes</legend>
        <input id="viewspan_notes" class="borderless" readonly="readonly"/>
      </fieldset>
    </form>
    <!-- Span dialog (view+edit) -->
    <form id="{base_id}_span_form" class="dialog" title="Span">
      <!-- Span dialog annotated text -->
      <fieldset id="span_selected_fset">
        <legend>Text</legend>
        <a target="brat_linked" id="span_highlight_link" href="#">Link</a>
        <div id="span_selected"/>
      </fieldset>
      <!-- Span dialog search links -->
      <fieldset id="span_search_fieldset">
        <legend>Search</legend>
        <div id="span_search_links"/>
      </fieldset>
      <!-- Span dialog type selector -->
      <fieldset>
        <div id="entity_and_event_wrapper" class="split_wrapper">
          <div id="span_entity_section" class="wrapper_half_left">
            <div id="entity_label" class="label-like">Entity type</div>
            <div id="entity_types" class="scroll_wrapper_upper">
              <div class="scroller"/>
            </div>
            <!-- NOTE: the attribute labels must be *outside* of the
                 divs they logically belong to prevent scrollers
                 overflowing them. -->
            <div id="entity_attribute_label"
                 class="label-like wrapper_lower_label">Entity attributes</div>
            <div id="entity_attributes" class="scroll_wrapper_lower">
              <div class="scroller small-buttons"/>
            </div>
          </div><div id="span_event_section" class="wrapper_half_right">
            <div id="event_label" class="label-like">Event type</div>
            <div id="event_types" class="scroll_wrapper_upper">
              <div class="scroller"/>
            </div>
            <div id="event_attribute_label"
                 class="wrapper_lower_label label-like">Event attributes</div>
            <div id="event_attributes" class="scroll_wrapper_lower">
              <div class="scroller small-buttons"/>
            </div>
          </div>
        </div>
      </fieldset>
      <!-- Span dialog normalization -->
      <fieldset id="norm_fieldset">
        <legend>Normalization</legend>
        <div id="norm_container">
          <select id="span_norm_db"/>
          <a id="span_norm_db_link" target="brat_linked" href="#" title="Search DB"><img src="`+fugueShadowlessMagnifierPng+`" style="vertical-align: middle"/></a>
          <span class="span_norm_label">ID:</span>
          <input id="span_norm_id" class="span_norm_id_input"
                 style="width:20%"/>
          <span class="span_norm_label">Ref:</span>
          <input id="span_norm_txt" class="span_norm_txt_input"
                 readonly="readonly" style="width:45%"
                 placeholder="Click here to search"/>
          <a id="span_norm_ref_link" target="brat_linked" href="#" title="See in DB"><img src="`+fugueShadowlessExternalPng+`" style="vertical-align: middle"/></a>
          <input id="clear_norm_button" type="button"
                 value="&#x2715;" title="Clear normalization"/>
        </div>
      </fieldset>
      <!-- Span dialog notes -->
      <fieldset>
        <legend>Notes</legend>
        <div id="span_notes_container">
          <input id="span_notes" class="borderless"/>
          <input id="clear_span_notes_button" type="button"
                 value="&#x2715;" title="Clear notes"/>
        </div>
      </fieldset>
    </form>
    <!-- Rapid mode span dialog -->
    <form id="{base_id}_rapid_span_form" class="dialog" title="Span type">
      <fieldset id="rapid_span_selected_fset">
        <legend>Text</legend>
        <div id="rapid_span_selected"/>
      </fieldset>
      <div id="rapid_span_types" class="scroll_fset" style="height:250px">
        <fieldset>
          <legend>Select type</legend>
          <div class="scroller" id="rapid_span_types_div">
            <!-- filled dynamically -->
          </div>
        </fieldset>
      </div>
    </form>
    <!-- Arc dialog -->
    <form id="{base_id}_arc_form" class="dialog" title="Arc">
      <fieldset id="arc_origin_fset">
        <legend>From</legend>
        <a target="brat_linked" id="arc_highlight_link" href="#">Link</a>
        <div id="arc_origin"/>
      </fieldset>

      <fieldset id="arc_target_fset">
        <legend>To</legend>
        <div id="arc_target"/>
      </fieldset>

      <div id="arc_roles" class="scroll_fset">
        <fieldset>
          <legend>Type</legend>
          <div class="scroller"/>
        </fieldset>
      </div>

      <fieldset id="arc_notes_fieldset">
        <legend>Notes</legend>
        <div id="arc_notes_container">
          <input id="arc_notes" class="borderless"/>
          <input id="clear_arc_notes_button" type="button"
                  value="&#x2715;" title="Clear notes"/>
        </div>
      </fieldset>

    </form>
    <!-- Login dialog -->
    <form id="{base_id}_auth_form" class="dialog" title="Login">
      <fieldset>
        <legend>Username</legend>
        <input id="auth_user" placeholder="Username" class="borderless"/>
      </fieldset>
      <fieldset>
        <legend>Password</legend>
        <input id="auth_pass" type="password" placeholder="Password" class="borderless"/>
      </fieldset>
    </form>
    <!-- Split span annotation dialog -->
    <form id="{base_id}_split_form" class="dialog" title="Split the Span">
      <fieldset>
        <legend>Split Roles</legend>
        <div id="split_roles" class="scroll_fset"/>
      </fieldset>
    </form>
    <!-- Browser dialog -->
    <form id="{base_id}_collection_browser" class="dialog" title="Open">
      <fieldset>
        <legend>Collection</legend>
        <input id="collection_input" readonly="readonly" placeholder="Document" class="borderless"/>
      </fieldset>
      <fieldset>
        <legend>Collection Information</legend>
        <div id="readme_container">
          <input id="readme" readonly="readonly" class="borderless"/>
          <input id="more_readme_button" type="button" value="More..." title="Show full collection information text"/>
        </div>
      </fieldset>
      <fieldset>
        <legend>Document</legend>
        <input id="document_input" placeholder="Document" class="borderless"/>
      </fieldset>
      <table id="document_select" class="ui-widget unselectable">
        <thead class="ui-widget-header"/>
        <tbody class="ui-widget-content"/>
      </table>
    </form>
    <!-- Normalization DB search dialog -->
    <form id="{base_id}_norm_search_dialog" class="dialog" title="Search">
      <fieldset>
        <legend>Query</legend>
        <div id="norm_search_container">
          <input id="norm_search_query" placeholder="Query string" class="borderless"/>
          <input id="norm_search_button" type="button" value="Search"/>
        </div>
      </fieldset>
      <fieldset>
        <legend>ID</legend>
        <input id="norm_search_id" placeholder="Identifier" class="borderless" readonly="readonly"/>
      </fieldset>
      <table id="norm_search_result_select" class="ui-widget unselectable">
        <thead class="ui-widget-header"/>
        <tbody class="ui-widget-content"/>
      </table>
    </form></div>`;
            return this.get_interpolat_dom(strForms);
        },

        get_messages_div_str: function () {
            //noinspection JSAnnotator
            var strMessages = `<div id='{base_id}_messa_cont'>
    <img id="{base_id}_spinner" src="`+spinnerGif+`"/>
    <div id="{base_id}_messagepullup" class="messages" style="display: none"/>
    <div id="{base_id}_messages" class="messages"/>
    <div id="{base_id}_pulluptrigger"/>
    <div id="{base_id}_waiter" class="dialog" title="Please wait">
      <img src="`+spinnerGif+`"/>
    </div>
</div>`;
            return this.get_interpolat_dom(strMessages);
        }
    })
;


module.exports = {
    VisualizerModel: VisualizerModel,
    AnnotatorModel: AnnotatorModel,
    VisualizerView: VisualizerView,
    AnnotatorView: AnnotatorView
};
