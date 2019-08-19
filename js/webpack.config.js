var fs = require('fs-extra');
var path = require('path');
var version = require('./package.json').version;
var webpack = require("webpack");
// var CopyPlugin = require('copy-webpack-plugin');
//var brat_fonts_selector = /fonts\/*\.(svg|ttf)/;
// Custom webpack rules are generally the same for all webpack bundles, hence
// stored in a separate local variable.
var rules = [
    { test: /\.css$/, use: ['style-loader', 'css-loader'] },
    { test: /\.json$/, loader: 'json-loader' },
    // Generic file loader, Should be used for anything but leaflet's
    // marker-icon.png, marker-icon-2x.png or marker-shadow.png
    { test: /\.(jpe?g|png|gif)$/, loader: 'file-loader' },
    { test: /static\/fonts\/.*\.(svg|ttf)$/, loader: 'file-loader', options: {name: 'static/fonts/[name].[ext]'} },
    { test: /[\/\\]src[\/\\]lib[\/\\]webfont\.js$/, use: ["imports-loader?this=>window"]}
]

// The static file directory.
var staticDir = path.resolve(__dirname, '..', 'brat_widget', 'static');


// Copy the package.json to static so we can inspect its version.
fs.copySync('./package.json', path.join(staticDir, 'package.json'))


module.exports = [
    {// Notebook extension
        //
        // This bundle only contains the part of the JavaScript that is run on
        // load of the notebook. This section generally only performs
        // some configuration for requirejs, and provides the legacy
        // "load_ipython_extension" function which is required for any notebook
        // extension.
        //
        entry: './src/extension.js',
        output: {
            filename: 'extension.js',
            path: staticDir,
            libraryTarget: 'amd'
        }
    },
    {// Bundle for the notebook containing the custom widget views and models
        //
        // This bundle contains the implementation for the custom widget views and
        // custom widget.
        // It must be an amd module
        //
        entry: './src/index.js',
        output: {
            filename: 'index.js',
            path: staticDir,
            libraryTarget: 'amd'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        externals: ['@jupyter-widgets/base'],
        node: {
            fs: 'empty',
            child_process: 'empty'
        },
        plugins: [
            // new CopyPlugin([
            //     { from: './src/static/fonts', to: 'static/fonts' },
            //     { from: './src/static/img', to: 'static/img' },
            //     { from: './src/static/jquery-theme/images', to: 'static/jquery-theme/images' },
            // ]),
            new webpack.ProvidePlugin({
                jQuery: "jquery"
            })
        ]
    },
    {// Embeddable brat-widget bundle
        //
        // This bundle is generally almost identical to the notebook bundle
        // containing the custom widget views and models.
        //
        // The only difference is in the configuration of the webpack public path
        // for the static assets.
        //
        // It will be automatically distributed by unpkg to work with the static
        // widget embedder.
        //
        // The target bundle is always `dist/index.js`, which is the path required
        // by the custom widget embedder.
        //
        entry: './src/embed.js',
        output: {
            filename: 'index.js',
            path: path.resolve(__dirname, 'dist'),
            libraryTarget: 'amd',
            publicPath: 'https://unpkg.com/brat-widget@' + version + '/dist/'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        externals: ['@jupyter-widgets/base'],
        node: {
            fs: 'empty',
            child_process: 'empty'
        },
        plugins: [
            // new CopyPlugin([
            //     { from: './src/static/fonts', to: 'static/fonts' },
            //     { from: './src/static/img', to: 'static/img' },
            //     { from: './src/static/jquery-theme/images', to: 'static/jquery-theme/images' },
            // ]),
            new webpack.ProvidePlugin({
                jQuery: "jquery"
            })
        ]
    },
    {// Bundle for the jupyterlab extension
        //
        // This bundle is generally almost identical to the notebook bundle
        // containing the custom widget views and models.
        //
        entry: './src/jupyterlab-plugin.js',
        output: {
            filename: 'jupyterlab-plugin.js',
            path: path.resolve(__dirname, '..', 'brat_widget', 'static'),
            libraryTarget: 'amd'
        },
        devtool: 'source-map',
        module: {
            rules: rules
        },
        externals: ['@jupyter-widgets/base'],
        node: {
            fs: 'empty',
            child_process: 'empty'
        },
        plugins: [
            // new CopyPlugin([
            //     { from: './src/static/fonts', to: 'static/fonts' },
            //     { from: './src/static/img', to: 'static/img' },
            //     { from: './src/static/jquery-theme/images', to: 'static/jquery-theme/images' },
            // ]),
            new webpack.ProvidePlugin({
                jQuery: "jquery"
            })
        ]
    }
];
