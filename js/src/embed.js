// Entry point for the unpkg bundle containing custom model definitions.
//
// It differs from the notebook bundle in that it does not need to define a
// dynamic baseURL for the static assets and may load some css that would
// already be loaded by the notebook otherwise.

// Export widget models and views, and the npm package version number.

module.exports = {};

var loadedModules = [

    require('./lib/head.load.min.js'),
/*
    require('./lib/jquery.min.js'),
    require('./lib/jquery-ui.min.js'),
    require('./lib/jquery-ui.combobox.js'),
    require('./lib/jquery.svg.min.js'),
    require('./lib/jquery.svgdom.min.js'),
    require('./lib/jquery.ba-bbq.min.js'),
    require('./lib/jquery.json.min.js'),
    require('./lib/sprintf.js'),
    require('./lib/webfont.js'),
    // brat helper modules
    require('./brat/configuration.js'),
    require('./brat/util.js'),
    require('./brat/annotation_log.js'),
    // brat modules
    require('./brat/dispatcher.js'),
    require('./brat/url_monitor.js'),
    require('./brat/ajax.js'),
    require('./brat/visualizer.js'),
    require('./brat/visualizer_ui.js'),
    require('./brat/annotator_ui.js'),
    require('./brat/spinner.js'),
*/
    // Export widget models and views, and the npm package version number.
    require('./example.js')
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

//module.exports = require('./example.js');
module.exports['version'] = require('../package.json').version;
