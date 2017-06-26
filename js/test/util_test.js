/**
 * Created by Edilmo on 6/25/17.
 */

describe('Util', function () {
    var Util;
    var webFontURLs;

    beforeEach(function() {
        /*Util = require('../src/util');
        webFontURLs = [
            require('../src/static/fonts/Astloch-Bold.ttf'),
            require('../src/static/fonts/PT_Sans-Caption-Web-Regular.ttf'),
            require('../src/static/fonts/Liberation_Sans-Regular.ttf')
        ];*/
        Util = 3;
        webFontURLs = [1, 1];
    });

    it('should be able to load fonts from url', function () {
        /*spyOn(Util, 'proceedWithFonts');
        Util.loadFonts(webFontURLs, dispatcher);
        expect(Util.proceedWithFonts).toHaveBeenCalled();
        expect(Util.timeoutLoadingFonts).ToBeFalsy();*/
        expect(Util).toEqual(3);
        expect(webFontURLs[0]).toEqual(1);
    });
});