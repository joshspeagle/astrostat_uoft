const fs = require('fs');
const path = require('path');
const { escapeHtml } = require('./shell');

/**
 * Renders the Research page from data/research.json.
 *
 * Returns `{ body, index }` like build/render-people.js: the page's HTML, and
 * the rows the "On this page" index is built from - here each carrying the
 * theme's icon, since eight recurring identities is the one case the canon
 * says iconography earns.
 *
 * Theme rosters are lists of *ids* into data/people.json, so a name, a short
 * form or a personal-site URL is written once, on the People page, and a
 * roster entry that names nobody fails the build instead of quietly drifting.
 */

const ROWS = [
  ['members', 'Members', 'members'],
  ['associates', 'Associates', 'associates'],
  ['collaborators', 'Collaborators', 'collaborators'],
];

/** id -> { id, name, short } for everyone on the People page. */
function loadPeople(peopleFile) {
  const data = JSON.parse(fs.readFileSync(peopleFile, 'utf8'));
  const index = new Map();
  for (const section of data.sections) {
    for (const person of section.people) index.set(person.id, person);
  }
  return index;
}

/**
 * How a person is written in a roster: their `short` form if the data file
 * gives one, otherwise their name with any parenthetical dropped - a card
 * headed "Mairead Heiger (Ph.D. 2026)" is just "Mairead Heiger" in a list.
 */
function rosterName(person) {
  return person.short || person.name.replace(/\s*\([^)]*\)/g, '').trim();
}

function renderRoster(entries, label, role, people, theme) {
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
    const link = `<a href="/people.html#${escapeHtml(id)}">${escapeHtml(rosterName(person))}</a>`;
    const note = typeof entry === 'string' ? null : entry.note;
    return note ? `${link} <span class="roster-note">(${escapeHtml(note)})</span>` : link;
  });

  // The second channel is fill, not hue: filled is inside the group, open is
  // affiliated, absent is outside - an order, drawn as one. The words never go
  // away; the square is never the only channel.
  return [
    `    <p class="roster-row ${role}">`,
    `      <span class="roster-label label"><span class="roster-mark" aria-hidden="true">`
    + `</span>${label}</span>`,
    `      <span class="roster-names">${names.join(', ')}</span>`,
    '    </p>',
  ];
}

function renderResearch(dataFile, peopleFile) {
  const dir = path.resolve(__dirname, '..', 'data');
  const data = JSON.parse(fs.readFileSync(dataFile || path.join(dir, 'research.json'), 'utf8'));
  const people = loadPeople(peopleFile || path.join(dir, 'people.json'));

  const out = [];
  const index = [];
  out.push(`<h1>${escapeHtml(data.title)}</h1>`);
  out.push('<div class="intro">');
  for (const para of data.intro) out.push(`  <p>${para}</p>`);
  out.push('</div>');

  const seen = new Set();

  for (const theme of data.themes) {
    if (!theme.id) throw new Error(`data/research.json: theme "${theme.title}" has no "id"`);
    if (seen.has(theme.id)) throw new Error(`data/research.json: duplicate theme id "${theme.id}"`);
    seen.add(theme.id);
    const id = escapeHtml(theme.id);
    index.push({ id: theme.id, title: theme.title, icon: theme.id });

    // One fixed image side, always the right-hand column. The page used to
    // alternate, which made the reader re-find the text column eight times.
    out.push('');
    out.push(`<section class="theme${theme.image ? '' : ' no-figure'}" id="${id}" data-spy>`);
    out.push(`  <h2><svg class="icon" aria-hidden="true" focusable="false">`
      + `<use href="#icon-${id}"></use></svg>${escapeHtml(theme.title)}</h2>`);
    out.push('  <div class="theme-prose">');
    for (const para of theme.paragraphs) out.push(`    <p>${para}</p>`);
    out.push('  </div>');

    if (theme.image) {
      out.push('  <figure class="theme-figure">');
      out.push(`    <img src="/static/${escapeHtml(theme.image)}" `
        + `alt="${escapeHtml(theme.alt)}" width="500" height="500" `
        + 'loading="lazy" decoding="async">');
      if (theme.credit) {
        // The credit is a caption, not prose: quiet, small, and not italic.
        out.push(`    <figcaption class="quiet">Image credit: ${escapeHtml(theme.credit)}`
          + '</figcaption>');
      }
      out.push('  </figure>');
    }

    out.push('  <div class="roster quiet-links">');
    for (const [key, label, role] of ROWS) {
      const entries = theme[key] || [];
      if (!entries.length) continue;   // a row with nobody in it says nothing
      out.push(...renderRoster(entries, label, role, people, theme.title));
    }
    out.push('  </div>');
    out.push('</section>');
  }

  return { body: out.join('\n'), index };
}

module.exports = { renderResearch, rosterName };
