const fs = require('fs');
const path = require('path');

/**
 * Renders the Research page body from data/research.json.
 *
 * Like the People page (see build/render-people.js) this is wired into
 * webpack.config.js as a `content` generator rather than a `filename`; the
 * output is a plain HTML string injected into main.ejs as the `body` partial.
 *
 * Theme rosters are lists of *ids* into data/people.json, so a name, a short
 * form or a personal-site URL is written once, on the People page, and a
 * roster entry that names nobody fails the build instead of quietly drifting.
 */

// Prose (`intro`, a theme's `paragraphs`) is raw HTML, exactly as on the People
// page. Everything else - titles, alt text, credits, names - is plain text.
function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

const ROWS = [
  ['members', 'ART members involved'],
  ['associates', 'ART associates involved'],
  ['collaborators', 'Collaborators include'],
];

/** id -> { id, name, short } for everyone on the People page. */
function loadPeople(peopleFile) {
  const data = JSON.parse(fs.readFileSync(peopleFile, 'utf8'));
  const index = new Map();
  for (const section of data.sections) {
    for (const person of section.people) {
      index.set(person.id, person);
    }
  }
  return index;
}

/**
 * How a person is written in a roster: their `short` form if the data file
 * gives one, otherwise their name with any parenthetical dropped — a card
 * headed "Mairead Heiger (Ph.D. '26)" is just "Mairead Heiger" in a list.
 */
function rosterName(person) {
  return person.short || person.name.replace(/\s*\([^)]*\)/g, '').trim();
}

function renderRoster(entries, label, people, theme) {
  const names = entries.map((entry) => {
    const id = typeof entry === 'string' ? entry : entry.id;
    const person = people.get(id);
    if (!person) {
      throw new Error(
        `data/research.json: theme "${theme}" lists "${id}" under `
        + `"${label}", which is not an id in data/people.json`);
    }
    // Every roster name points at the person's own card. The personal-site
    // link lives there, written once, rather than being re-typed per theme.
    const link = `<a href="/people.html#${id}">${escapeHtml(rosterName(person))}</a>`;
    const note = typeof entry === 'string' ? null : entry.note;
    return note ? `${link} <span class="roster-note">(${escapeHtml(note)})</span>` : link;
  });

  return [
    '    <p class="roster-row">',
    `      <strong>${label}:</strong>`,
    `      <span class="roster-names">${names.join(', ')}</span>`,
    '    </p>',
  ];
}

function renderResearch(dataFile, peopleFile) {
  const dir = path.resolve(__dirname, '..', 'data');
  const data = JSON.parse(fs.readFileSync(dataFile || path.join(dir, 'research.json'), 'utf8'));
  const people = loadPeople(peopleFile || path.join(dir, 'people.json'));

  const out = [];
  out.push('<section class="small-12">');
  out.push('');
  out.push(`  <h1>${escapeHtml(data.title)}</h1>`);
  for (const para of data.intro) {
    out.push('');
    out.push('  <p>');
    out.push(`    ${para}`);
    out.push('  </p>');
  }

  const seen = new Set();

  data.themes.forEach((theme, i) => {
    if (!theme.id) throw new Error(`data/research.json: theme "${theme.title}" has no "id"`);
    if (seen.has(theme.id)) throw new Error(`data/research.json: duplicate theme id "${theme.id}"`);
    seen.add(theme.id);

    // The images alternate sides. That used to fall out of an :nth-child(odd)
    // rule counting headings, spacer <br>s and roster blocks, which meant the
    // side a theme landed on depended on how many siblings happened to precede
    // it. It is stated here instead, so it survives a theme being added or moved.
    const flip = i % 2 === 1 ? ' media-flip' : '';

    out.push('');
    const id = escapeHtml(theme.id);
    out.push(`  <h2 id="${id}" data-icon="${id}">${escapeHtml(theme.title)}</h2>`);
    out.push('');
    out.push(`  <div class="media-object stack-for-small${flip}">`);
    out.push('    <div class="media-object-section">');
    out.push('      <figure class="theme-figure">');
    // A theme with no image on file renders src-less, exactly as a person with
    // no headshot does (build/render-people.js). js/index.js fills those in with
    // the palette placeholder; `src="/static/null"` would instead ask the server
    // for a file that cannot exist and show a broken image.
    const attrs = ['class="research-thumbnail"'];
    if (theme.image) attrs.push(`src="/static/${escapeHtml(theme.image)}"`);
    attrs.push(`alt="${escapeHtml(theme.alt)}"`, 'width="500"', 'height="500"', 'loading="lazy"');
    out.push(`        <img ${attrs.join(' ')}>`);
    if (theme.credit) {
      out.push(`        <figcaption class="credit">Image credit: ${escapeHtml(theme.credit)}</figcaption>`);
    }
    out.push('      </figure>');
    out.push('    </div>');
    out.push('    <div class="media-object-section main-section">');
    for (const para of theme.paragraphs) {
      out.push('      <p>');
      out.push(`        ${para}`);
      out.push('      </p>');
    }
    out.push('    </div>');
    out.push('  </div>');
    out.push('');
    out.push('  <div class="theme-roster">');
    for (const [key, label] of ROWS) {
      const entries = theme[key] || [];
      if (!entries.length) continue;   // a row with nobody in it says nothing
      out.push(...renderRoster(entries, label, people, theme.title));
    }
    out.push('  </div>');
  });

  out.push('');
  out.push('</section>');
  return out.join('\n');
}

module.exports = { renderResearch, rosterName };
