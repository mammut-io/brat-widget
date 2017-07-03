// -*- Mode: JavaScript; tab-width: 2; indent-tabs-mode: nil; -*-
// vim:set ft=javascript ts=2 sw=2 sts=2 cindent:
var Spinner = (function($, window, undefined) {
    var Spinner = function(dispatcher, spinElementPath) {
      var that = this;

      var count = 0;
      var spin = function() {
        var spinElement = $(spinElementPath);
        if (count === 0) {
          console.log("Spinner: spin.");
          spinElement.css('display', 'block');
        }
        count++;
      };
      var unspin = function() {
        var spinElement = $(spinElementPath);
        count--;
        if (count === 0) {
          console.log("Spinner: unspin.");
          spinElement.css('display', 'none');
        }
      };

      dispatcher.
          on('spin', spin).
          on('unspin', unspin);
    };

    return Spinner;
})(jQuery, window);

module.exports = Spinner;