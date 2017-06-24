var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

require('svg-jquery');

// brat jquery-theme
require('./static/jquery-theme/jquery-ui.css');
require('./static/jquery-theme/jquery-ui-redmond.css');
// brat
require('./static/style-vis.css');
require('./static/style-ui.css');
require('./static/style.css');

var webFontURLs = [
            require('./static/fonts/Astloch-Bold.ttf'),
            require('./static/fonts/PT_Sans-Caption-Web-Regular.ttf'),
            require('./static/fonts/Liberation_Sans-Regular.ttf')
        ];

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
        value : 'Hello World'
    })
});


// Custom View. Renders the widget model.
var VisualizerView = widgets.DOMWidgetView.extend({
    render: function() {
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    },

    value_changed: function() {
        var collData = {
            entity_types: [{
                type: 'Person',
                /* The labels are used when displaying the annotion, in this case
                 we also provide a short-hand "Per" for cases where
                 abbreviations are preferable */
                labels: ['Person', 'Per'],
                // Blue is a nice colour for a person?
                bgColor: '#7fa2ff',
                // Use a slightly darker version of the bgColor for the border
                borderColor: 'darken'
            }]
        };
        var docData = {
            // Our text of choice
            text: "Ed O'Kelley was the man who shot the man who shot Jesse James.",
            // The entities entry holds all entity annotations
            entities: [
                /* Format: [${ID}, ${TYPE}, [[${START}, ${END}]]]
                 note that range of the offsets are [${START},${END}) */
                ['T1', 'Person', [[0, 11]]],
                ['T2', 'Person', [[20, 23]]],
                ['T3', 'Person', [[37, 40]]],
                ['T4', 'Person', [[50, 61]]],
            ],
        };
        this.el.id = "brat_" + new Date().getTime().toString();
        console.log(_.isString(this.el));
        console.log(Util);

        Util.embed(this.el, collData, docData, webFontURLs);
        //this.el.textContent = this.model.get('value');
        //this.el.innerHTML = this.model.get('value').bold();
    }
});


module.exports = {
    VisualizerModel : VisualizerModel,
    VisualizerView : VisualizerView
};
