var widgets = require('jupyter-js-widgets');
var _ = require('underscore');

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

        //console.log(util.toString());

        //util.Util.embed(this.el, collData, docData, webFontURLs);
        //require('./brat/util.js');
        //Util.embed(this.el, collData, docData, webFontURLs);
        //this.el.textContent = util.hasOwnProperty('Util').toString();
        //this.el.textContent = this.model.get('value');
        //this.el.innerHTML = this.model.get('value').bold();

        this.el.innerHTML = `<div id="embedding-entity-example" class="hasSVG" style="display: block; height: 48.546875px;"><svg version="1.1" class="" style="width: 970px; height: 48.546875px;"><!-- document: undefined/undefined --><defs><filter id="Gaussian_Blur"><fegaussianblur in="SourceGraphic" stddeviation="2"></fegaussianblur></filter><marker id="drag_arrow" refX="5" refY="2.5" markerWidth="5" markerHeight="5" orient="auto" markerUnits="strokeWidth" class="drag_fill"><polyline points="0,0 5,2.5 0,5 0.2,2.5"></polyline></marker></defs><g class="background"><rect x="0" y="4.1875" width="970" height="46.546875" class="background0"></rect></g><g class="glow"></g><g class="highlight"><rect x="24" y="31.953125" width="77.900390625" height="15.78125" fill="#e5ecfe" rx="3" ry="3"></rect><rect x="161.42724609375" y="31.953125" width="29.1796875" height="15.78125" fill="#e5ecfe" rx="3" ry="3"></rect><rect x="283.328125" y="31.953125" width="29.1796875" height="15.78125" fill="#e5ecfe" rx="3" ry="3"></rect><rect x="380.376953125" y="31.953125" width="87.53173828125" height="15.78125" fill="#e5ecfe" rx="3" ry="3"></rect></g><g class="text"><text x="0" y="0"><tspan x="24" y="44.546875" data-chunk-id="0">Ed O'Kelley </tspan><tspan x="105.900390625" y="44.546875" data-chunk-id="1">was </tspan><tspan x="136.5751953125" y="44.546875" data-chunk-id="2">the </tspan><tspan x="161.42724609375" y="44.546875" data-chunk-id="3" class="">man </tspan><tspan x="194.60693359375" y="44.546875" data-chunk-id="4">who </tspan><tspan x="226.1240234375" y="44.546875" data-chunk-id="5">shot </tspan><tspan x="258.47607421875" y="44.546875" data-chunk-id="6">the </tspan><tspan x="283.328125" y="44.546875" data-chunk-id="7">man </tspan><tspan x="316.5078125" y="44.546875" data-chunk-id="8">who </tspan><tspan x="348.02490234375" y="44.546875" data-chunk-id="9">shot </tspan><tspan x="380.376953125" y="44.546875" data-chunk-id="10">Jesse James.</tspan></text></g><g transform="translate(0, 44)"><g></g><g transform="translate(24, 0)"><g></g><g class="span"><rect x="20.5" y="-29.28125" width="37.62999725341797" height="10.765625" class="span_Person span_default" fill="#7fa2ff" stroke="#002998" rx="2" ry="1" data-span-id="T1" data-fragment-id="0"></rect><text x="38.5" y="-20.78125" fill="#000000">Person</text><path d="M0,-13.515625C0,-17.515625 38.5,-13.515625 38.5,-17.515625C38.5,-13.515625 77.900390625,-17.515625 77.900390625,-13.515625" class="curly" stroke="#002998"></path></g></g><g transform="translate(105.900390625, 0)"><g></g></g><g transform="translate(136.5751953125, 0)"><g></g></g><g transform="translate(161.42724609375, 0)"><g></g><g class="span"><rect x="4.5" y="-29.28125" width="19.920000076293945" height="10.765625" class="span_Person span_default" fill="#7fa2ff" stroke="#002998" rx="2" ry="1" data-span-id="T2" data-fragment-id="0"></rect><text x="14.5" y="-20.78125" fill="#000000">Per</text><path d="M0,-13.515625C0,-17.515625 14.5,-13.515625 14.5,-17.515625C14.5,-13.515625 29.1796875,-17.515625 29.1796875,-13.515625" class="curly" stroke="#002998"></path></g></g><g transform="translate(194.60693359375, 0)"><g></g></g><g transform="translate(226.1240234375, 0)"><g></g></g><g transform="translate(258.47607421875, 0)"><g></g></g><g transform="translate(283.328125, 0)"><g></g><g class="span"><rect x="4.5" y="-29.28125" width="19.920000076293945" height="10.765625" class="span_Person span_default" fill="#7fa2ff" stroke="#002998" rx="2" ry="1" data-span-id="T3" data-fragment-id="0"></rect><text x="14.5" y="-20.78125" fill="#000000">Per</text><path d="M0,-13.515625C0,-17.515625 14.5,-13.515625 14.5,-17.515625C14.5,-13.515625 29.1796875,-17.515625 29.1796875,-13.515625" class="curly" stroke="#002998"></path></g></g><g transform="translate(316.5078125, 0)"><g></g></g><g transform="translate(348.02490234375, 0)"><g></g></g><g transform="translate(380.376953125, 0)"><g></g><g class="span"><rect x="24.5" y="-29.28125" width="37.62999725341797" height="10.765625" class="span_Person span_default" fill="#7fa2ff" stroke="#002998" rx="2" ry="1" data-span-id="T4" data-fragment-id="0"></rect><text x="43.5" y="-20.78125" fill="#000000">Person</text><path d="M0,-13.515625C0,-17.515625 43.5,-13.515625 43.5,-17.515625C43.5,-13.515625 87.53173828125,-17.515625 87.53173828125,-13.515625" class="curly" stroke="#002998"></path></g></g><g class="arcs"></g></g><g class="sentnum"><a NS1:href="#undefined?focus=sent~1"><text x="18" y="44.546875" data-sent="1">1</text></a><path d="M20,0L20,48.546875"></path></g></svg></div>`;

    }
});


module.exports = {
    VisualizerModel : VisualizerModel,
    VisualizerView : VisualizerView
};
