// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/brat-widget/';

module.exports = {};

var loadedModules = [
    // brat fonts
    require('./static/fonts/Astloch-Bold.ttf'),
    require('./static/fonts/Liberation_Sans-Regular.svg'),
    require('./static/fonts/Liberation_Sans-Regular.ttf'),
    require('./static/fonts/PT_Sans-Caption-Web-Regular.svg'),
    require('./static/fonts/PT_Sans-Caption-Web-Regular.ttf'),
    // brat img
    require('./static/img/arrow.png'),
    require('./static/img/arrow-180.png'),
    require('./static/img/collapse_icon.gif'),
    require('./static/img/expand_icon.gif'),
    require('./static/img/Fugue-document.png'),
    require('./static/img/Fugue-folder-horizontal-open.png'),
    require('./static/img/Fugue-shadowless-document.png'),
    require('./static/img/Fugue-shadowless-exclamation.png'),
    require('./static/img/Fugue-shadowless-exclamation-white.png'),
    require('./static/img/Fugue-shadowless-external.png'),
    require('./static/img/Fugue-shadowless-folder-horizontal-open.png'),
    require('./static/img/Fugue-shadowless-information-balloon.png'),
    require('./static/img/Fugue-shadowless-magnifier.png'),
    require('./static/img/Fugue-shadowless-question.png'),
    require('./static/img/spinner.gif'),
    //brat lib
    require('jquery'),
    require('./lib/jquery.svg.min.js'),
    require('./lib/webfont.js'),
    require('jquery-ui'),
    require('jquery-ui.combobox'),
    // brat
    require('./static/style-vis.css'),
    require('./static/style-ui.css'),
    //brat code
    require('./ajax.js'),
    require('./annotation_log.js'),
    require('./annotator_ui.js'),
    require('./configuration.js'),
    require('./dispatcher.js'),
    require('./offline_ajax.js'),
    require('./spinner.js'),
    require('./url_monitor.js'),
    require('./util.js'),
    require('./visualizer.js'),
    require('./visualizer_ui.js'),

    // Export widget models and views, and the npm package version number.
    require('./widget.js')
];

for (var i in loadedModules) {
    if (loadedModules.hasOwnProperty(i)) {
        var loadedModule = loadedModules[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}

module.exports['version'] = require('../package.json').version;
