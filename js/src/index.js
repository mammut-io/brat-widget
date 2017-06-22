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
/*
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
    // brat jquery-theme/images
    require('./static/jquery-theme/images/ui-bg_flat_0_aaaaaa_40x100.png'),
    require('./static/jquery-theme/images/ui-bg_flat_55_fbec88_40x100.png'),
    require('./static/jquery-theme/images/ui-bg_glass_75_d0e5f5_1x400.png'),
    require('./static/jquery-theme/images/ui-bg_glass_85_dfeffc_1x400.png'),
    require('./static/jquery-theme/images/ui-bg_glass_95_fef1ec_1x400.png'),
    require('./static/jquery-theme/images/ui-bg_gloss-wave_55_5c9ccc_500x100.png'),
    require('./static/jquery-theme/images/ui-bg_inset-hard_100_f5f8f9_1x100.png'),
    require('./static/jquery-theme/images/ui-bg_inset-hard_100_fcfdfd_1x100.png'),
    require('./static/jquery-theme/images/ui-icons_2e83ff_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_6da8d5_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_217bc0_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_469bdd_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_cd0a0a_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_d8e7f3_256x240.png'),
    require('./static/jquery-theme/images/ui-icons_f9bd01_256x240.png'),

    // brat jquery-theme
    require('./static/jquery-theme/jquery-ui.css'),
    require('./static/jquery-theme/jquery-ui-redmond.css'),

    // brat head js
    require('./lib/head.load.min.js'),

    require('jquery'),
    require('./lib/jquery.min.js'),
    require('./lib/jquery-ui.min.js'),
    require('./lib/jquery-ui.combobox.js'),
    require('./lib/jquery.svg.min.js'),
    require('./lib/jquery.svgdom.min.js'),
    require('./lib/jquery.ba-bbq.min.js'),
    require('./lib/jquery.json.min.js'),
    require('./lib/sprintf.js'),
    require('./lib/webfont.js'),
*/
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

module.exports['version'] = require('../package.json').version;
