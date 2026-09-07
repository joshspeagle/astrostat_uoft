const fs = require('fs');
const path = require('path');

/**
 * Renders the People page body from data/people.json.
 *
 * The output is a plain HTML string injected into main.ejs as the `body`
 * partial (see webpack.config.js). Indentation here is cosmetic only —
 * html-webpack-plugin minifies the final page — but it is kept readable so
 * that `npx webpack` output stays diffable during review.
 */
// A paragraph that is nothing but a link — by convention the person's website,
// the first paragraph of an entry. It is tagged so the stylesheet can set it as
// a label (see `.card p.person-link` in scss/index.scss). Styling the first
// paragraph by position instead put the whole bio in small caps for the entries
// that have no website to lead with.
const LINK_ONLY = /^<a\b[^>]*>[^<]*<\/a>$/;

// name, alt, heading and title are plain text in the data file; only
// `paragraphs` is documented as raw HTML. Escaping the rest keeps a stray
// quote or ampersand in a name from corrupting the markup around it.
// (Kept local rather than shared with render-research.js: two five-line
// helpers are cheaper than a third module in build/.)
function escapeHtml(value) {
  return String(value == null ? '' : value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// "Postdoctoral Researchers" -> "postdoctoral-researchers", for the heading's
// id. Person ids come from the data file, not from here.
function slug(value) {
  return String(value)
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^A-Za-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase();
}

// The data file names a section's layout by intent; the Foundation grid classes
// that implement it live here, so a column count is a rendering decision rather
// than content. `compact` is the denser treatment used for the roster-like
// sections (Collaborators, Recent Alumni), whose entries are a name and a line
// or two rather than a bio; the design pass may take it further.
const LAYOUTS = {
  faculty: 'small-up-1 medium-up-2',
  cards: 'small-up-1 medium-up-3',
  compact: 'small-up-1 medium-up-4',
};

// Headshots in static/ are square (add_headshot.py enforces it) and served at
// 500px. Stating that here gives the browser an aspect ratio to reserve before
// the image loads, which stops the roster reflowing as it fills in.
const HEADSHOT_PX = 500;

function renderPeople(dataFile) {
  const file = dataFile || path.resolve(__dirname, '..', 'data', 'people.json');
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));

  const out = [];
  out.push('<section class="small-12">');
  out.push('');
  out.push(`  <h1>${escapeHtml(data.title)}</h1>`);
  out.push('');
  out.push('  <p>');
  out.push(`    ${data.intro}`);
  out.push('  </p>');

  const seen = new Set();

  for (const section of data.sections) {
    const layout = section.layout || 'cards';
    const grid = LAYOUTS[layout];
    if (!grid) {
      throw new Error(
        `data/people.json: section "${section.heading}" has unknown layout `
        + `"${layout}" (expected one of ${Object.keys(LAYOUTS).join(', ')})`);
    }
    const sectionId = slug(section.heading);

    out.push('');
    out.push('  <br>');
    out.push('');
    out.push(`  <h2 id="${sectionId}">${escapeHtml(section.heading)}</h2>`);
    out.push('');
    out.push(`  <div class="grid-x grid-margin-x ${grid}">`);

    for (const person of section.people) {
      if (!person.id) {
        throw new Error(`data/people.json: "${person.name}" has no "id"`);
      }
      if (seen.has(person.id)) {
        throw new Error(`data/people.json: duplicate id "${person.id}"`);
      }
      seen.add(person.id);

      const attrs = ['class="person-thumbnail"'];
      if (person.image) attrs.push(`src="/static/${escapeHtml(person.image)}"`);
      if (person.alt) attrs.push(`alt="${escapeHtml(person.alt)}"`);
      attrs.push(`width="${HEADSHOT_PX}"`, `height="${HEADSHOT_PX}"`, 'loading="lazy"');

      out.push('');
      out.push(`    <div class="cell" id="${escapeHtml(person.id)}" data-section="${sectionId}">`);
      out.push('      <div class="card">');
      out.push(`        <img ${attrs.join(' ')}>`);
      out.push('        <div class="card-section">');
      out.push(`          <span class="h3">${escapeHtml(person.name)}</span>`);
      for (const p of person.paragraphs) {
        const cls = LINK_ONLY.test(p.trim()) ? ' class="person-link"' : '';
        out.push(`          <p${cls}>${p}</p>`);
      }
      out.push('        </div>');
      out.push('      </div>');
      out.push('    </div>');
    }

    out.push('');
    out.push('  </div>');
  }

  out.push('');
  out.push('</section>');
  return out.join('\n');
}

module.exports = { renderPeople };
