const fs = require('fs');
const path = require('path');
const { escapeHtml, slug } = require('./shell');

const CJK_RE = /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/;

// Wrap parenthetical suffixes so they do not break across lines inside the
// parentheses; tag CJK parentheticals so they scale cleanly beside Latin type.
function displayName(name) {
  return escapeHtml(name).replace(/\(([^()]+)\)/g, (_, inner) => {
    const cls = CJK_RE.test(inner) ? 'nowrap card-name-cjk' : 'nowrap';
    return `<span class="${cls}">(${inner})</span>`;
  });
}

// Compute 2-letter monogram initials for entries without a headshot photo,
// ignoring parenthetical nicknames or degree notes.
function initialsFor(name) {
  const bare = String(name || '')
    .replace(/\([^)]*\)/g, ' ')
    .replace(/[^A-Za-z\u00C0-\u017F\s-]+/g, ' ')
    .trim();
  const tokens = bare.split(/\s+/).filter(Boolean);
  if (!tokens.length) return 'ART';
  if (tokens.length === 1) return tokens[0].slice(0, 2).toUpperCase();
  return (tokens[0][0] + tokens[tokens.length - 1][0]).toUpperCase();
}

/**
 * Renders the People page from data/people.json.
 *
 * Returns `{ body, index }`: the page's HTML and the rows used to build the
 * "On this page" index.
 */

const LINK_ONLY = /^<a\b[^>]*>[^<]*<\/a>$/;
const LINK_PARTS = /^<a\b([^>]*)>([^<]*)<\/a>$/;
const NOTE_ONLY = /^<(b|strong)\b[^>]*>(?:(?!<\/\1>)[\s\S])*<\/\1>$/;

const LAYOUTS = { faculty: 'card', cards: 'card', compact: 'compact' };
const HEADSHOT_PX = 500;

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
    const initials = escapeHtml(initialsFor(person.name));
    return `<div class="${cls} no-photo" aria-hidden="true">`
      + `<span class="no-photo-initials">${initials}</span></div>`;
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
    '      <div class="card-text quiet-links">',
    `        <h3 class="card-name">${displayName(person.name)}</h3>`,
  ];
  if (site) out.push(`        <p class="card-site"><a ${site.attrs}>${site.text}</a></p>`);
  if (note) out.push(`        <p class="card-note">${note}</p>`);
  for (const p of bio) out.push(`        <p class="card-bio">${p}</p>`);
  out.push('      </div>', '    </div>');
  return out;
}

function compactRow(person, sectionId, withPhoto) {
  const { site, note, bio } = parts(person);
  const name = displayName(person.name);
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

    const withPhoto = form === 'compact' && section.people.every((p) => p.image);
    let gridClass = 'card-grid';
    if (form === 'compact') {
      gridClass = 'compact-list quiet-links';
    } else if (layout === 'faculty') {
      gridClass = 'card-grid card-grid-faculty';
    }

    out.push('');
    out.push(`<section class="people-section" id="${id}" data-spy>`);
    out.push(`  <h2>${escapeHtml(section.heading)}</h2>`);
    out.push(`  <div class="${gridClass}">`);

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
