const fs = require('fs');
const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssoWebpackPlugin = require('csso-webpack-plugin').default;
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

const pages = [
  {
    name: 'index',
    title: 'Astrostat@UofT',
    partials: [
      {
        name: 'body',
        filename: './ejs/pages/home/body.html',
      },
      {
        name: 'crumbs',
        filename: './ejs/pages/home/crumbs.html',
      },
    ],
  },
  {
    name: 'people',
    title: 'Astrostat@UofT | People',
    partials: [
      {
        name: 'body',
        filename: './ejs/pages/people/body.html',
      },
      {
        name: 'crumbs',
        filename: './ejs/pages/people/crumbs.html',
      },
    ],
  },
  {
    name: 'research',
    title: 'Astrostat@UofT | Research',
    partials: [
      {
        name: 'body',
        filename: './ejs/pages/research/body.html',
      },
      {
        name: 'crumbs',
        filename: './ejs/pages/research/crumbs.html',
      },
    ],
  },
];

const htmlPlugins = pages.map((page) => {
  return new HtmlWebpackPlugin({
    filename: `${page.name}.html`,
    template: './ejs/main.ejs',
    inject: 'body',
    publicPath: '/',
    base: '/',
    chunks: [
      'index',
      'defaultVendors',
    ],
    templateParameters: {
      pageTitle: page.title || '',
      partials: (page.partials || []).reduce((acc, cur) => {
        return {
          ...acc,
          [cur.name]: fs.readFileSync(cur.filename),
        };
      }, {}),
    },
  });
});

module.exports = {
  target: 'web',
  mode: 'production',
  entry: {
    index: {
      library: {
        name: 'index',
        type: 'var',
      },
      import: [
        './scss/index.scss',
        './js/index.js',
      ],
    },
  },
  module: {
    rules: [
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'assets/fonts-[name][ext]',
        },
      },
      {
        test: /\.svg$/,
        type: 'asset/inline',
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
        ],
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          {
            loader: 'sass-loader',
            options: {
              implementation: 'sass',
              sassOptions: {
                indentWidth: 2,
                alertColor: true,
                quietDeps: true,
              },
            },
          },
        ],
      },
      {
        test: /\.js$/,
        use: [
          'babel-loader',
        ],
      },
      {
        test: /\.ejs$/,
        use: [
          {
            loader: 'ejs-loader',
            options: {
              esModule: false,
            },
          },
        ],
      },
    ],
  },
  optimization: {
    minimize: true,
    sideEffects: true,
  },
  resolve: {
    alias: {
      fdn: path.resolve(__dirname, 'node_modules/foundation-sites'),
    },
    modules: ['node_modules'],
  },
  plugins: [
    new webpack.ProgressPlugin(),
    new MiniCssExtractPlugin({
      filename: 'assets/[name].css',
    }),
    new CssoWebpackPlugin(),
    ...htmlPlugins,
    new CopyPlugin({
      patterns: [
        {
          from: './static',
          to: 'static',
        },
      ],
    }),
  ],
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: (pathData) => {
      return `assets/${pathData.chunk.name.split('/')[0]}.bundle.js`;
    },
    clean: true,
  },
};

// vim: set ft=javascript:
