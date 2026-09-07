const fs = require('fs');
const path = require('path');
const { escapeHtml, slug } = require('./shell');

// A trailing parenthetical in a name - "Joshua S. Speagle (沈佳士)", "Isabelle (Liyuan) Huang"
// - must not break across lines inside the parentheses. Escape first, then wrap.
function displayName(name) {
  return escapeHtml(name).replace(/\(([^()]+)\)/g, '<span class="nowrap">($1)</span>');
}

/**
 * Renders the People page from data/people.json.
 *
 * Returns `{ body, index }`: the page's HTML, and the rows the "On this page"
 * index is built from, so the index cannot drift from the sections it points
 * at. Wired into webpack.config.js as a `render` function rather than a
 * `filename` - there is no ejs/pages/people/body.html.
 *
 * Two forms, chosen by the section's `layout`:
 *
 *   card    (faculty, cards) - photo, name, website label line, status note,
 *           bio, in that fixed order, in one grid module for every section.
 *   compact (compact)        - one row per person: a small square photo, the
 *           name as the link to their site, then the bio at the small step.
 */

// A paragraph that is nothing but a link - by convention the person's website,
// and the first paragraph of an entry. On a card it becomes the website label
// line; on a compact row it is what makes the name a link.
const LINK_ONLY = /^<a\b[^>]*>[^<]*<\/a>$/;
const LINK_PARTS = /^<a\b([^>]*)>([^<]*)<\/a>$/;

// A status note - "On leave November 2025-2026." - is a paragraph that is
// nothing but bold text. It is emphasis, and emphasis on this site is bold.
// One bold run and nothing else - not "a bold start ... and <b>more</b>".
const NOTE_ONLY = /^<(b|strong)\b[^>]*>(?:(?!<\/\1>)[\s\S])*<\/\1>$/;

const LAYOUTS = { faculty: 'card', cards: 'card', compact: 'compact' };

// Headshots in static/ are square (add_headshot.py enforces it) and served at
// 500px. Stating that here gives the browser a ratio to reserve before the
// image loads, so the grid does not reflow as it fills in.
const HEADSHOT_PX = 500;

/** Split an entry's paragraphs into the card's fixed order. */
function parts(person) {
  const paragraphs = person.paragraphs.slice();
  let site = null;
  if (paragraphs.length && LINK_ONLY.test(paragraphs[0].trim())) {
    const m = LINK_PARTS.exec(paragraphs.shift().trim());
    site = { attrs: m[1].trim(), text: m[2] };
  }
  let note = null;
  if (paragraphs.length && NOTE_ONLY.test(paragraphs[0].trim())) {
    note = paragraphs.shift().trim();
  }
  return { site, note, bio: paragraphs };
}

function photo(person, cls) {
  if (!person.image) {
    // No src is ever emitted for a missing photo: an <img> without one is
    // invalid, and the canon says an image that is not there shows its surface
    // and nothing else.
    return `<div class="${cls} no-photo" aria-hidden="true"></div>`;
  }
  const attrs = [
    `class="${cls}"`,
    `src="/static/${escapeHtml(person.image)}"`,
    `alt="${escapeHtml(person.alt || '')}"`,
    `width="${HEADSHOT_PX}"`,
    `height="${HEADSHOT_PX}"`,
    'loading="lazy"',
    'decoding="async"',
  ];
  return `<img ${attrs.join(' ')}>`;
}

function card(person, sectionId) {
  const { site, note, bio } = parts(person);
  const out = [
    `    <div class="card" id="${escapeHtml(person.id)}" data-section="${sectionId}">`,
    `      ${photo(person, 'card-photo')}`,
    '      <div class="card-text">',
    `        <h3 class="card-name">${displayName(person.name)}</h3>`,
  ];
  // The repeated first line of ~50 cards is demoted into the small-caps label
  // idiom rather than weakened as a link: it is still a real, dotted,
  // link-token link, just no longer a body-size sentence fifty times over.
  if (site) out.push(`        <p class="card-site"><a ${site.attrs}>${site.text}</a></p>`);
  if (note) out.push(`        <p class="card-note">${note}</p>`);
  for (const p of bio) out.push(`        <p class="card-bio">${p}</p>`);
  out.push('      </div>', '    </div>');
  return out;
}

function compactRow(person, sectionId, withPhoto) {
  const { site, note, bio } = parts(person);
  const name = displayName(person.name);
  // On a one-line row the name is the only thing worth clicking, so it carries
  // the link; on a card the name is a heading and headings are not links.
  const heading = site
    ? `<a class="compact-name" ${site.attrs}>${name}</a>`
    : `<span class="compact-name">${name}</span>`;

  const out = [`    <div class="compact-row" id="${escapeHtml(person.id)}" `
    + `data-section="${sectionId}">`];
  if (withPhoto) out.push(`      ${photo(person, 'compact-photo')}`);
  out.push('      <div class="compact-text">', `        ${heading}`);
  for (const p of (note ? [note].concat(bio) : bio)) {
    out.push(`        <p class="compact-bio">${p}</p>`);
  }
  out.push('      </div>', '    </div>');
  return out;
}

function renderPeople(dataFile) {
  const file = dataFile || path.resolve(__dirname, '..', 'data', 'people.json');
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));

  const out = [];
  const index = [];
  out.push(`<h1>${escapeHtml(data.title)}</h1>`);
  out.push('<div class="intro">');
  out.push(`  <p class="lede">${data.intro}</p>`);
  out.push('</div>');

  const seen = new Set();

  for (const section of data.sections) {
    const layout = section.layout || 'cards';
    const form = LAYOUTS[layout];
    if (!form) {
      throw new Error(
        `data/people.json: section "${section.heading}" has unknown layout `
        + `"${layout}" (expected one of ${Object.keys(LAYOUTS).join(', ')})`);
    }
    if (!section.people || !section.people.length) continue;
    const id = slug(section.heading);
    if (seen.has(id)) {
      throw new Error(`data/people.json: section "${section.heading}" slugs to "${id}", which is already used`);
    }
    seen.add(id);
    index.push({ id, title: section.heading, count: section.people.length });

    // A compact row carries a thumbnail only when every entry in the section
    // has one; a row of ragged blanks reads worse than no photos at all.
    const withPhoto = form === 'compact' && section.people.every((p) => p.image);

    out.push('');
    out.push(`<section class="people-section" id="${id}" data-spy>`);
    out.push(`  <h2>${escapeHtml(section.heading)}</h2>`);
    out.push(`  <div class="${form === 'compact' ? 'compact-list quiet-links' : 'card-grid'}">`);

    for (const person of section.people) {
      if (!person.id) throw new Error(`data/people.json: "${person.name}" has no "id"`);
      if (seen.has(person.id)) throw new Error(`data/people.json: duplicate id "${person.id}"`);
      seen.add(person.id);
      out.push(...(form === 'compact'
        ? compactRow(person, id, withPhoto)
        : card(person, id)));
    }

    out.push('  </div>');
    out.push('</section>');
  }

  return { body: out.join('\n'), index };
}

module.exports = { renderPeople };
