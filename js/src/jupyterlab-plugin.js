var bratWidget = require('./index');
require("./static/style.css");
require('./static/style-vis.css');
require('./static/style-ui.css');

var base = require('@jupyter-widgets/base');

/**
 * The widget manager provider.
 */
module.exports = {
  id: 'brat-widget',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'brat-widget',
          version: bratWidget.version,
          exports: bratWidget
      });
    },
  autoStart: true
};