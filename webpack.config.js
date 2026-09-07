const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssoWebpackPlugin = require('csso-webpack-plugin').default;
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const { renderPeople } = require('./build/render-people');
const { renderResearch } = require('./build/render-research');

// The home page's "last updated" line used to be a hand-typed date, and was only
// ever as fresh as the last person who remembered to change it. Take it from the
// content itself: the date of the newest commit touching the data files or the
// page partials.
//
// That only works with real history behind the checkout. `actions/checkout`
// clones at depth 1 unless the workflow asks for more, and on a shallow clone
// the tip is a root commit: git diffs it against the empty tree, every path
// matches, and the pathspec silently degrades to "the date of this commit" -
// i.e. the last push to main, CSS- and CI-only commits included. Rather than
// report that as a content date, say so in the build log; the fix is
// `fetch-depth: 0` on the checkout step in .github/workflows/*.yaml.
function git(args) {
  try {
    return execSync(`git ${args}`, {
      cwd: __dirname,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    }).trim();
  } catch (e) {
    return '';
  }
}

function lastUpdated() {
  // A shallow clone is only a problem when it is shallow enough to have no
  // history to search: at depth 1 the single commit is a root commit, so every
  // path "changed" in it. A deeper truncated clone (a dev container is often
  // one) answers the pathspec perfectly well, so test the commit count rather
  // than the shallow flag.
  const rootOnly = git('rev-list --count HEAD') === '1';
  if (rootOnly) {
    console.warn(
      '[last-updated] depth-1 checkout: git cannot see which commit last '
      + 'touched data/ or ejs/pages/, so the home page will show the date of '
      + 'this build\'s commit. Set fetch-depth: 0 on the checkout step for the '
      + 'real content date.');
  }
  // With no history the pathspec is meaningless (see above), so drop it and take
  // the tip date directly - same answer, without implying it means more.
  let stamp = git(rootOnly ? 'log -1 --format=%cs' : 'log -1 --format=%cs -- data ejs/pages');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(stamp)) {
    // No git at all (a tarball export): today is the best available answer.
    stamp = new Date().toISOString().slice(0, 10);
  }
  const [y, m, d] = stamp.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC',
  });
}

const LAST_UPDATED = lastUpdated();

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
        // Generated from data/people.json - see build/render-people.js
        name: 'body',
        content: renderPeople,
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
        // Generated from data/research.json - see build/render-research.js
        name: 'body',
        content: renderResearch,
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
    favicon: './ico/favicon.ico',
    inject: 'body',
    publicPath: '/',
    chunks: [
      'index',
      'defaultVendors',
    ],
    templateParameters: {
      pageTitle: page.title || '',
      partials: (page.partials || []).reduce((acc, cur) => {
        const html = cur.content
          ? cur.content()
          : fs.readFileSync(cur.filename, 'utf8');
        return {
          ...acc,
          [cur.name]: html.replace(/\{\{LAST_UPDATED\}\}/g, LAST_UPDATED),
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
        test: /\.ico/,
        type: 'asset/resource',
        generator: {
          filename: 'assets/[name][ext]',
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
