const fs = require('fs');
const path = require('path');

/**
 * The pieces of the page shell that are data-driven, built in Node.
 *
 * `ejs/main.ejs` is compiled by html-webpack-plugin's lodash template loader,
 * which interpolates strings but is a poor place to loop. Anything with a list
 * in it - the site nav, the in-page index, the icon sprite - is assembled here
 * and injected as one string, which is also what keeps the two copies of the
 * index (the rail's and the narrow-width disclosure's) built from one array.
 */

const SVG_DIR = path.resolve(__dirname, '..', 'svg');

function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/** "Postdoctoral Researchers" -> "postdoctoral-researchers". */
function slug(value) {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^A-Za-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase();
}

/**
 * The palette, read back out of scss/_tokens.scss.
 *
 * The canon says a hex value lives in exactly one place. The stylesheet is that
 * place, so the two <meta name="theme-color"> tags and the web-app manifest -
 * which are markup, not CSS - take their values from it rather than restating
 * them. docs/check_tokens.py parses the same block for the same reason.
 */
function readTokens() {
  const src = fs.readFileSync(
    path.resolve(__dirname, '..', 'scss', '_tokens.scss'), 'utf8');
  const themes = {};
  const block = /(light|dark):\s*\(([^)]*)\)/g;
  let m;
  while ((m = block.exec(src)) !== null) {
    const entries = {};
    const pair = /([a-z]+):\s*(#[0-9a-fA-F]{6})/g;
    let p;
    while ((p = pair.exec(m[2])) !== null) entries[p[1]] = p[2];
    themes[m[1]] = entries;
  }
  for (const name of ['light', 'dark']) {
    if (!themes[name] || !themes[name].page) {
      throw new Error(`scss/_tokens.scss: could not read the ${name} palette`);
    }
  }
  return themes;
}

/**
 * The ART mark as a <symbol>, from svg/art-mark.svg. The file holds the path
 * once, with no fill, so the mark is drawn in whatever token the element that
 * references it is set to - the wash in the hero, the mark token in the rail.
 * F014: one copy per page, however many times it is drawn.
 */
let MARK_VIEWBOX = null;

function markSymbol() {
  const src = fs.readFileSync(path.join(SVG_DIR, 'art-mark.svg'), 'utf8');
  const viewBox = /viewBox="([^"]+)"/.exec(src);
  const inner = /<svg[^>]*>([\s\S]*)<\/svg>/.exec(src);
  if (!viewBox || !inner) {
    throw new Error('svg/art-mark.svg: expected a single <svg viewBox="...">...</svg>. '
      + 'If it looks like a Git LFS pointer, run `git lfs pull`.');
  }
  if (/\sfill="/.test(src)) {
    throw new Error('svg/art-mark.svg: a baked fill would stop the mark taking its token');
  }
  [, MARK_VIEWBOX] = viewBox;
  return `<symbol id="art-mark" viewBox="${MARK_VIEWBOX}">${inner[1].trim()}</symbol>`;
}

/** The eight Research theme glyphs, as <symbol>s, exactly as authored. */
function themeSymbols() {
  const src = fs.readFileSync(path.join(SVG_DIR, 'themes-sprite.svg'), 'utf8');
  const inner = /<svg[^>]*>([\s\S]*)<\/svg>/.exec(src);
  if (!inner) {
    throw new Error('svg/themes-sprite.svg: expected one wrapping <svg>. '
      + 'If it looks like a Git LFS pointer, run `git lfs pull`.');
  }
  return inner[1].trim();
}

/**
 * One hidden <svg> per page holding every symbol that page draws. The theme
 * glyphs only ship on Research, where they are used.
 */
function sprite({ themes = false } = {}) {
  const parts = [markSymbol()];
  if (themes) parts.push(themeSymbols());
  return '<svg class="sprite" aria-hidden="true" focusable="false">'
    + parts.join('') + '</svg>';
}

function use(id, cls) {
  return `<svg class="${cls}" aria-hidden="true" focusable="false">`
    + `<use href="#${id}"></use></svg>`;
}

/**
 * A drawing of the mark. The outer <svg> restates the symbol's viewBox (read
 * from the file, not typed) so it has an intrinsic ratio and `width: 100%;
 * height: auto` sizes it correctly.
 */
function markSvg() {
  if (!MARK_VIEWBOX) markSymbol();
  return `<svg class="mark-svg" viewBox="${MARK_VIEWBOX}" aria-hidden="true" `
    + 'focusable="false"><use href="#art-mark"></use></svg>';
}

// The external mark, on Statstro alone. Drawn on the icon grid - 24px box,
// 2px stroke, round joins, no fill, currentColor - like every other glyph.
const EXTERNAL = '<svg class="icon icon-inline" aria-hidden="true" focusable="false" '
  + 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
  + 'stroke-linecap="round" stroke-linejoin="round">'
  + '<path d="M8 16 16 8"/><path d="M10 8h6v6"/></svg>';

// The four destinations, in the canon's order, identical on every page.
const DESTINATIONS = [
  { key: 'home', text: 'Home', href: '/' },
  { key: 'people', text: 'People', href: '/people.html' },
  { key: 'research', text: 'Research', href: '/research.html' },
  { key: 'statstro', text: 'Statstro', href: 'https://statstro.com/', external: true },
];

/**
 * The site nav. The current page is marked three ways - ink, bold, and a
 * hairline quiet bar on the leading edge - never by colour alone. Statstro is
 * the one destination that leaves the site and the one that takes the external
 * mark; its accessible name says so.
 */
function siteNav(current) {
  const items = DESTINATIONS.map((d) => {
    const on = d.key === current;
    const attrs = [`href="${d.href}"`];
    if (on) attrs.push('aria-current="page"');
    let text = escapeHtml(d.text);
    if (d.external) {
      attrs.push(`aria-label="${escapeHtml(d.text)} (external site)"`);
      text += EXTERNAL;
    }
    return `<li${on ? ' class="is-current"' : ''}><a ${attrs.join(' ')}>${text}</a></li>`;
  });
  // Not a landmark of its own: the whole rail is the "Site" navigation region
  // (the canon's order - mark, destinations, switch, index - is what the region
  // is), and this is the destinations part of it.
  return '<div class="rail-nav rail-group">'
    + '<h2 class="label">Navigate</h2>'
    + `<ul>${items.join('')}</ul></div>`;
}

/**
 * One in-page index row. `items` come from the page's renderer, so the index
 * cannot drift from the sections it points at: People carry a count, Research
 * carries the theme's icon.
 */
function indexRow(item) {
  const icon = item.icon ? use(`icon-${escapeHtml(item.icon)}`, 'icon') : '';
  const count = item.count === undefined ? ''
    : `<span class="index-count">${item.count}</span>`;
  return `<li><a href="#${escapeHtml(item.id)}" data-spy-for="${escapeHtml(item.id)}">`
    + `${icon}<span class="index-name">${escapeHtml(item.title)}</span>${count}</a></li>`;
}

/** The rail's copy: a labelled navigation landmark beside the content. */
function railIndex(items) {
  if (!items || !items.length) return '';
  return '<nav class="rail-index rail-group" aria-label="On this page">'
    + '<h2 class="label">On this page</h2>'
    + `<ul class="index">${items.map(indexRow).join('')}</ul></nav>`;
}

/**
 * The narrow-width copy: a native disclosure under the h1. Not a landmark -
 * the rail's nav is the one "On this page" region, and two would be two.
 */
function pageIndex(items) {
  if (!items || !items.length) return '';
  return '<details class="otp"><summary><span class="label">On this page</span>'
    + '<svg class="chevron" aria-hidden="true" focusable="false" viewBox="0 0 24 24" '
    + 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
    + 'stroke-linejoin="round"><path d="M6 9.5 12 15.5 18 9.5"/></svg></summary>'
    + `<ol class="index">${items.map(indexRow).join('')}</ol></details>`;
}

/**
 * A hand-written partial indexes itself: every h1/h2 that carries an id and
 * data-spy is a section the rail can point at. Titles come from the heading
 * text with any markup stripped.
 */
function indexFromMarkup(html) {
  const out = [];
  const re = /<h([12])\b([^>]*)>([\s\S]*?)<\/h\1>/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const attrs = m[2];
    const id = (attrs.match(/\bid="([^"]+)"/) || [])[1];
    if (!id || !/\bdata-spy\b/.test(attrs)) continue;
    const title = m[3].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
    out.push({ id, title });
  }
  return out;
}

/**
 * schema.org structured data. Every page carries the group as an Organization;
 * the People page adds its current members as Person entries whose @id is the
 * card anchor, so search engines can tie a name to this site. Generated from
 * data/people.json, the same source the page is built from.
 */
const CURRENT_SECTIONS = new Set([
  'Faculty', 'Postdoctoral Researchers', 'Graduate Students',
  'Undergraduate Students', 'ART Associates',
]);
const LINK_ONLY = /^<a\s+href="([^"]+)"[^>]*>[^<]*<\/a>$/;

function jsonld(page, origin) {
  const org = {
    '@type': 'Organization',
    '@id': `${origin}/#organization`,
    name: 'Astrostatistics Research Team',
    alternateName: ['ART', 'Astrostat@UofT'],
    url: `${origin}/`,
    logo: `${origin}/icon-512.png`,
    parentOrganization: {
      '@type': 'CollegeOrUniversity',
      name: 'University of Toronto',
      url: 'https://www.utoronto.ca/',
    },
  };
  const graph = [org];
  if (page.name === 'people') {
    const people = JSON.parse(fs.readFileSync(path.resolve(__dirname, '..', 'data', 'people.json'), 'utf8'));
    for (const section of people.sections) {
      if (!CURRENT_SECTIONS.has(section.heading)) continue;
      for (const person of section.people) {
        const entry = {
          '@type': 'Person',
          '@id': `${origin}/people.html#${person.id}`,
          name: person.name.replace(/\s*\([^)]*\)\s*$/, ''),
          affiliation: { '@id': org['@id'] },
        };
        const first = (person.paragraphs || [])[0] || '';
        const link = first.trim().match(LINK_ONLY);
        if (link) entry.url = link[1];
        if (person.image) entry.image = `${origin}/static/${person.image}`;
        graph.push(entry);
      }
    }
  }
  const doc = { '@context': 'https://schema.org', '@graph': graph };
  // A literal "</script" inside the JSON would end the element early.
  return JSON.stringify(doc).replace(/</g, '\\u003c');
}

module.exports = {
  escapeHtml,
  readTokens,
  slug,
  sprite,
  markSvg,
  siteNav,
  railIndex,
  pageIndex,
  indexFromMarkup,
  jsonld,
  DESTINATIONS,
};
