var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'brat-widget',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'brat-widget',
          version: plugin.version,
          exports: plugin
      });
    },
  autoStart: true
};