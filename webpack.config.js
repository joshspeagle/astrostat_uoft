const path = require('path');
const { execSync } = require('child_process');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssoWebpackPlugin = require('csso-webpack-plugin').default;
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');
const { renderHome } = require('./build/render-home');
const { renderPeople } = require('./build/render-people');
const { renderResearch } = require('./build/render-research');
const shell = require('./build/shell');

const ORIGIN = 'https://astrostatuoft.com';

// Compute the "last updated" date from the most recent commit touching data/ or ejs/.
// Requires `fetch-depth: 0` on CI checkouts so git log can inspect commit history.
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
  const rootOnly = git('rev-list --count HEAD') === '1';
  if (rootOnly) {
    console.warn(
      '[last-updated] depth-1 checkout: git cannot see which commit last '
      + 'touched data/ or ejs/, so the site footer will show the date of '
      + "this build's commit. Set fetch-depth: 0 on the checkout step for the "
      + 'content commit date.');
  }
  let stamp = git(rootOnly ? 'log -1 --format=%cs' : 'log -1 --format=%cs -- data ejs');
  if (!/^\d{4}-\d{2}-\d{2}$/.test(stamp)) {
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
    render: renderHome,
  },
  {
    name: 'people',
    title: 'Astrostat@UofT | People',
    nav: 'people',
    url: '/people.html',
    description: 'Faculty, postdocs, students, associates, collaborators, and recent '
      + 'alumni of the Astrostatistics Research Team at the University of Toronto.',
    render: renderPeople,
  },
  {
    name: 'research',
    title: 'Astrostat@UofT | Research',
    nav: 'research',
    url: '/research.html',
    themeIcons: true,
    description: 'Research themes of the Astrostatistics Research Team at the University '
      + 'of Toronto: inference, stellar evolution, dark matter, AI for science, the Milky '
      + 'Way, galaxies, transients, and star formation.',
    render: renderResearch,
  },
  {
    name: '404',
    title: 'Astrostat@UofT | Page not found',
    nav: null,
    url: '/404.html',
    noindex: true,
    description: 'Page not found. Navigate to the Home, People, or Research pages of the '
      + 'Astrostatistics Research Team at the University of Toronto.',
    body: '<h1>Page not found</h1>\n'
      + '<div class="intro"><p class="lede">There is nothing at this address. It may have '
      + 'moved, or the link that brought you here may be out of date. Try the '
      + '<a href="/">home page</a>, the <a href="/people.html">people</a> in the group, or '
      + 'the <a href="/research.html">research</a> we do.</p></div>',
  },
];

const htmlPlugins = pages.map((page) => {
  const rendered = page.render ? page.render() : null;
  const bodyBase = rendered ? rendered.body : (page.body || '');
  const index = rendered ? rendered.index : shell.indexFromMarkup(bodyBase);

  const disclosure = shell.pageIndex(index);
  let body = bodyBase;
  if (disclosure) {
    body = body.includes('</h1>')
      ? body.replace('</h1>', `</h1>\n${disclosure}`)
      : `${disclosure}\n${body}`;
  }

  return new HtmlWebpackPlugin({
    filename: `${page.name}.html`,
    template: './ejs/main.ejs',
    inject: 'body',
    publicPath: '/',
    chunks: ['index'],
    templateParameters: {
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
 * Emit root-level crawler and manifest files (robots.txt, sitemap.xml,
 * site.webmanifest) directly from the page list and token definitions.
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
 * Replace `{{LAST_UPDATED}}` in ejs/main.ejs after template rendering so the
 * placeholder remains inspectable in source checks.
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
  performance: {
    hints: false,
  },
  resolve: {
    modules: ['node_modules'],
  },
  plugins: [
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
