var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

// brat jquery-theme styles
require('./static/jquery-theme/jquery-ui.css');
require('./static/jquery-theme/jquery-ui-redmond.css');
// brat styles
require('./static/style-vis.css');
require('./static/style-ui.css');
require('./static/style.css');
//brat fonts
var webFontURLs = [
            require('file-loader!./static/fonts/Astloch-Bold.ttf'),
            require('file-loader!./static/fonts/PT_Sans-Caption-Web-Regular.ttf'),
            require('file-loader!./static/fonts/Liberation_Sans-Regular.ttf')
        ];
//brat modules
var Visualizer = require('./visualizer');
var Dispatcher = require('./dispatcher');

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
        _model_name : 'VisualizerModel',
        _view_name : 'VisualizerView',
        _model_module : 'brat-widget',
        _view_module : 'brat-widget',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
        collection : {},
        value : {}
    })
});


// Custom View. Renders the widget model.
var VisualizerView = widgets.DOMWidgetView.extend({
    render: function() {
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    },

    value_changed: function() {
        this.el.id = "brat_" + new Date().getTime().toString();
        console.log(_.isString(this.el));

        this.embed(this.el, this.model.get('collection'), this.model.get('value'), webFontURLs);
    },

        // container: ID or jQuery element
    // collData: the collection data (in the format of the result of
    //   http://.../brat/ajax.cgi?action=getCollectionInformation&collection=...
    // docData: the document data (in the format of the result of
    //   http://.../brat/ajax.cgi?action=getDocument&collection=...&document=...
    // returns the embedded visualizer's dispatcher object
    embed: function(container, collData, docData, webFontURLs,
                         dispatcher) {
      if (dispatcher === undefined) {
          dispatcher = new Dispatcher();
      }
      var visualizer = new Visualizer(dispatcher, container, webFontURLs);
      docData.collection = null;
      dispatcher.post('collectionLoaded', [collData]);
      dispatcher.post('requestRenderData', [docData]);
      return dispatcher;
    }
});


module.exports = {
    VisualizerModel : VisualizerModel,
    VisualizerView : VisualizerView
};
