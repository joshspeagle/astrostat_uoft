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
function renderPeople(dataFile) {
  const file = dataFile || path.resolve(__dirname, '..', 'data', 'people.json');
  const data = JSON.parse(fs.readFileSync(file, 'utf8'));

  const out = [];
  out.push('<section class="small-12">');
  out.push('');
  out.push(`  <h1>${data.title}</h1>`);
  out.push('');
  out.push('  <p>');
  out.push(`    ${data.intro}`);
  out.push('  </p>');

  for (const section of data.sections) {
    out.push('');
    out.push('  <br>');
    out.push('');
    out.push(`  <h2>${section.heading}</h2>`);
    out.push('');
    out.push(`  <div class="grid-x grid-margin-x ${section.grid}">`);

    for (const person of section.people) {
      const attrs = ['class="person-thumbnail"'];
      if (person.image) attrs.push(`src="/static/${person.image}"`);
      if (person.alt) attrs.push(`alt="${person.alt}"`);

      out.push('');
      out.push('    <div class="cell">');
      out.push('      <div class="card">');
      out.push(`        <img ${attrs.join(' ')}>`);
      out.push('        <div class="card-section">');
      out.push(`          <span class="h3">${person.name}</span>`);
      for (const p of person.paragraphs) {
        out.push(`          <p>${p}</p>`);
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
