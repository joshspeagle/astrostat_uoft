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
const shell = require('./build/shell');

const ORIGIN = 'https://astrostatuoft.com';

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
      + "this build's commit. Set fetch-depth: 0 on the checkout step for the "
      + 'real content date.');
  }
  // With no history the pathspec is meaningless (see above), so drop it and take
  // the tip date directly - same answer, without implying it means more.
  let stamp = git(rootOnly ? 'log -1 --format=%cs' : 'log -1 --format=%cs -- data ejs');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(stamp)) {
    // No git at all (a tarball export): today is the best available answer.
    stamp = new Date().toISOString().slice(0, 10);
  }
  const [y, m, d] = stamp.split('-').map(Number);
  const text = new Date(Date.UTC(y, m - 1, d)).toLocaleDateString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC',
  });
  return { text, iso: stamp };
}

const UPDATED = lastUpdated();
const LAST_UPDATED = UPDATED.text;
const TOKENS = shell.readTokens();

// Every page: what it is called, what it says it is, and where its body comes
// from. `render` returns { body, index }; `partial` is a hand-written file.
const pages = [
  {
    name: 'index',
    title: 'Astrostat@UofT',
    nav: 'home',
    hero: true,
    url: '/',
    description: 'The Astrostatistics Research Team at the University of Toronto: '
      + 'statistics and machine learning for astronomical data, from single stars to '
      + 'cosmology.',
    partial: './ejs/pages/home/body.html',
  },
  {
    name: 'people',
    title: 'Astrostat@UofT | People',
    nav: 'people',
    url: '/people.html',
    description: 'Faculty, postdocs, students, associates, collaborators and recent '
      + 'alumni of the Astrostatistics Research Team at the University of Toronto.',
    render: renderPeople,
  },
  {
    name: 'research',
    title: 'Astrostat@UofT | Research',
    nav: 'research',
    url: '/research.html',
    themeIcons: true,
    description: 'What the Astrostatistics Research Team studies: inference, stellar '
      + 'evolution, dark matter, AI, the Milky Way, galaxies, transients and star '
      + 'formation.',
    render: renderResearch,
  },
  {
    // Not in the sitemap and not linked from anywhere: GitHub Pages serves it
    // for any URL that does not exist. Same shell, so a mistyped link from an
    // old CV lands somewhere that still knows the way back (F066).
    name: '404',
    title: 'Astrostat@UofT | Page not found',
    nav: null,
    url: '/404.html',
    noindex: true,
    description: 'There is nothing at this address. Find the home, people and research '
      + 'pages of the Astrostatistics Research Team at the University of Toronto.',
    body: '<h1>Page not found</h1>\n'
      + '<div class="intro"><p class="lede">There is nothing at this address. It may have '
      + 'moved, or the link that brought you here may be out of date. Try the '
      + '<a href="/">home page</a>, the <a href="/people.html">people</a> in the group, or '
      + 'the <a href="/research.html">research</a> we do.</p></div>',
  },
];

const htmlPlugins = pages.map((page) => {
  const rendered = page.render ? page.render() : null;
  let body = page.body || '';
  if (rendered) body = rendered.body;
  if (page.partial) body = fs.readFileSync(page.partial, 'utf8');
  // A hand-written partial indexes its own headings: any h1/h2 carrying an id
  // and data-spy is a section the rail can point at.
  const index = rendered ? rendered.index : shell.indexFromMarkup(body);

  // The narrow-width disclosure belongs directly under the page's own h1 - the
  // first thing every body renders - rather than above it.
  const disclosure = shell.pageIndex(index);
  if (disclosure) body = body.replace('</h1>', `</h1>\n${disclosure}`);

  return new HtmlWebpackPlugin({
    filename: `${page.name}.html`,
    template: './ejs/main.ejs',
    inject: 'body',
    publicPath: '/',
    chunks: ['index'],
    templateParameters: {
      // Escaped here, not in the template: html-webpack-plugin's lodash loader
      // interpolates raw, so an '&' or a quote in a title would otherwise break
      // the <meta> attributes or fail the minifier.
      title: shell.escapeHtml(page.title),
      description: shell.escapeHtml(page.description),
      canonical: ORIGIN + page.url,
      origin: ORIGIN,
      noindex: !!page.noindex,
      hero: !!page.hero,
      themeColorLight: TOKENS.light.page,
      themeColorDark: TOKENS.dark.page,
      sprite: shell.sprite({ themes: !!page.themeIcons }),
      mark: shell.markSvg(),
      siteNav: shell.siteNav(page.nav),
      railIndex: shell.railIndex(index),
      jsonld: shell.jsonld(page, ORIGIN),
      body,
    },
  });
});

/**
 * The three files that belong at the site root but are not pages: the crawler
 * rules, the list of canonical URLs, and the web-app manifest. Emitted from the
 * build rather than hand-committed, so the URL list cannot fall behind `pages`.
 */
class RootFiles {
  apply(compiler) {
    const { RawSource } = compiler.webpack.sources;
    compiler.hooks.thisCompilation.tap('RootFiles', (compilation) => {
      compilation.hooks.processAssets.tap({
        name: 'RootFiles',
        stage: compiler.webpack.Compilation.PROCESS_ASSETS_STAGE_ADDITIONAL,
      }, () => {
        const listed = pages.filter((p) => !p.noindex);
        // The content date, not the build date, so a rebuild does not tell
        // crawlers that every page changed.
        const today = UPDATED.iso;

        compilation.emitAsset('robots.txt', new RawSource(
          `User-agent: *\nAllow: /\n\nSitemap: ${ORIGIN}/sitemap.xml\n`));

        compilation.emitAsset('sitemap.xml', new RawSource(
          '<?xml version="1.0" encoding="UTF-8"?>\n'
          + '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + listed.map((p) => `  <url>\n    <loc>${ORIGIN}${p.url}</loc>\n`
            + `    <lastmod>${today}</lastmod>\n  </url>\n`).join('')
          + '</urlset>\n'));

        compilation.emitAsset('site.webmanifest', new RawSource(`${JSON.stringify({
          name: 'Astrostatistics Research Team - University of Toronto',
          short_name: 'Astrostat@UofT',
          icons: [
            { src: '/icon-512.png', sizes: '512x512', type: 'image/png' },
          ],
          theme_color: TOKENS.light.page,
          background_color: TOKENS.light.page,
          display: 'browser',
          start_url: '/',
        }, null, 2)}\n`));
      });
    });
  }
}

/**
 * `{{LAST_UPDATED}}` is written in ejs/main.ejs's site note and substituted
 * here, after the template has rendered, so the placeholder stays a plain
 * marker that scripts/audit_site.py and the update skill can both look for.
 */
class LastUpdated {
  apply(compiler) {
    compiler.hooks.compilation.tap('LastUpdated', (compilation) => {
      HtmlWebpackPlugin.getHooks(compilation).beforeEmit.tap('LastUpdated', (data) => {
        data.html = data.html.replace(/\{\{LAST_UPDATED\}\}/g, LAST_UPDATED);
        return data;
      });
    });
  }
}

module.exports = {
  target: 'web',
  mode: 'production',
  entry: {
    index: {
      import: [
        './scss/index.scss',
        './js/index.js',
      ],
    },
  },
  module: {
    rules: [
      {
        test: /\.(woff|woff2)$/,
        type: 'asset/resource',
        generator: {
          filename: 'assets/fonts-[name][ext]',
        },
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
    modules: ['node_modules'],
  },
  plugins: [
    new webpack.ProgressPlugin(),
    new MiniCssExtractPlugin({
      filename: 'assets/[name].css',
    }),
    new CssoWebpackPlugin(),
    ...htmlPlugins,
    new LastUpdated(),
    new RootFiles(),
    new CopyPlugin({
      patterns: [
        { from: './static', to: 'static' },
        // The favicon set belongs at the site root: `GET /favicon.ico` is still
        // how some readers and feed clients ask, and the manifest names
        // /icon-512.png.
        { from: './ico', to: '.' },
      ],
    }),
  ],
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: (pathData) => `assets/${pathData.chunk.name.split('/')[0]}.bundle.js`,
    clean: true,
  },
};

// vim: set ft=javascript:
