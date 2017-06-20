// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/brat-widget/';

// brat External libraries
/*var $ = require('./lib/jquery.min.js');
$ = $.extend(require('./lib/jquery-ui.min.js'));
$ = $.extend(require('./lib/jquery-ui.combobox.js'));
$ = $.extend(require('./lib/jquery.svg.min.js'));
$ = $.extend(require('./lib/jquery.svgdom.min.js'));
$ = $.extend(require('./lib/jquery.ba-bbq.min.js'));
$ = $.extend(require('./lib/jquery.json.min.js'));
$ = $.extend(require('./lib/sprintf.js'));
$ = $.extend(require('./lib/webfont.js'));
// brat helper modules
$ = $.extend(require('./brat/configuration.js'));
$ = $.extend(require('./brat/util.js'));
$ = $.extend(require('./brat/annotation_log.js'));
// brat modules
$ = $.extend(require('./brat/dispatcher.js'));
$ = $.extend(require('./brat/url_monitor.js'));
$ = $.extend(require('./brat/ajax.js'));
$ = $.extend(require('./brat/visualizer.js'));
$ = $.extend(require('./brat/visualizer_ui.js'));
$ = $.extend(require('./brat/annotator_ui.js'));
$ = $.extend(require('./brat/spinner.js'));

// Export widget models and views, and the npm package version number.
module.exports = $.extend(require('./example.js'));*/
module.exports = require('./example.js');
module.exports['version'] = require('../package.json').version;
