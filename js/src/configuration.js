// -*- Mode: JavaScript; tab-width: 2; indent-tabs-mode: nil; -*-
// vim:set ft=javascript ts=2 sw=2 sts=2 cindent:
var Configuration = (function(window, undefined) {
    var abbrevsOn = true;
    var textBackgrounds = "striped";
    var svgWidth = '100%';
    var rapidModeOn = false;
    var confirmModeOn = true;
    var autorefreshOn = false;
    var typeCollapseLimit = 30;
    
    var visual = {
      margin: {
          x: 2,
          y: 1,
          assign: function (config) {
              this.x = config.x;
              this.y = config.y;
          }
      },
      arcTextMargin: 1,
      boxSpacing: 1,
      curlyHeight: 4,
      arcSpacing: 9, //10;
      arcStartHeight: 19, //23; //25;
      assign: function (config) {
          this.margin.assign(config.margin);
          this.arcTextMargin = config.arcTextMargin;
          this.boxSpacing = config.boxSpacing;
          this.curlyHeight = config.curlyHeight;
          this.arcSpacing = config.arcSpacing;
          this.arcStartHeight = config.arcStartHeight;
      }
    };

    return {
      abbrevsOn: abbrevsOn,
      textBackgrounds: textBackgrounds,
      visual: visual,
      svgWidth: svgWidth,
      rapidModeOn: rapidModeOn,
      confirmModeOn: confirmModeOn,
      autorefreshOn: autorefreshOn,
      typeCollapseLimit: typeCollapseLimit,
      assign: function (config) {
          this.abbrevsOn = config.abbrevsOn;
          this.textBackgrounds = config.textBackgrounds;
          this.svgWidth = config.svgWidth;
          this.rapidModeOn = config.rapidModeOn;
          this.confirmModeOn = config.confirmModeOn;
          this.autorefreshOn = config.autorefreshOn;
          this.typeCollapseLimit = config.typeCollapseLimit;
          this.visual.assign(config.visual);
      }
    };
})(window);

module.exports = Configuration;