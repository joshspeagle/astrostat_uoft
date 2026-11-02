'use strict';

/**
 * Turn data/home.json into the body HTML and section index of the Home page.
 *
 * Keeps the Home page data-driven alongside People (data/people.json) and
 * Research (data/research.json). Paragraph strings and captions may contain
 * inline HTML (<b>, <strong>, <a>), matching the convention in the other data files.
 */

const fs = require('fs');
const path = require('path');

const DEFAULT_PATH = path.resolve(__dirname, '../data/home.json');

function renderFigure(fig) {
  if (!fig) return '';
  const attrs = [`src="${fig.src}"`];
  if (fig.srcset) attrs.push(`srcset="${fig.srcset}"`);
  if (fig.sizes) attrs.push(`sizes="${fig.sizes}"`);
  if (fig.width) attrs.push(`width="${fig.width}"`);
  if (fig.height) attrs.push(`height="${fig.height}"`);
  attrs.push('loading="lazy"', 'decoding="async"');
  attrs.push(`alt="${fig.alt || ''}"`);

  const caption = fig.caption
    ? `\n  <figcaption class="quiet">${fig.caption}</figcaption>`
    : '';
  return `<figure class="figure">
  <img ${attrs.join(' ')}>${caption}
</figure>`;
}

function renderAbout(about) {
  const lede = about.lede ? `<p class="lede">\n  ${about.lede}\n</p>` : '';
  const paras = (about.paragraphs || []).map((p) => `<p>\n  ${p}\n</p>`).join('\n\n');
  const fig = renderFigure(about.figure);
  return [
    `<h1 id="${about.id}" data-spy>\n  ${about.heading}\n</h1>`,
    lede,
    paras,
    fig,
  ].filter(Boolean).join('\n\n');
}

function renderWorkshop(workshop) {
  const paras = (workshop.paragraphs || []).map((p) => `<p>\n  ${p}\n</p>`).join('\n\n');
  const fig = renderFigure(workshop.figure);
  return [
    `<h2 id="${workshop.id}" data-spy>\n  ${workshop.heading}\n</h2>`,
    paras,
    fig,
  ].filter(Boolean).join('\n\n');
}

function renderJoining(joining) {
  const intro = (joining.intro || []).map((p) => `<p>\n  ${p}\n</p>`).join('\n\n');
  const cards = (joining.pathways || [])
    .map((pw) => {
      const paras = (pw.paragraphs || []).map((p) => `    <p>${p}</p>`).join('\n');
      let fellowships = '';
      if (pw.fellowships && pw.fellowships.length) {
        const items = pw.fellowships
          .map(
            (f) =>
              `      <li><a class="fellowship-pill" href="${f.url}">${f.label}</a></li>`
          )
          .join('\n');
        fellowships = `\n    <ul class="fellowship-list">\n${items}\n    </ul>`;
      }
      return `  <article class="pathway-card">
    <h3 class="pathway-title">${pw.heading}</h3>
${paras}${fellowships}
  </article>`;
    })
    .join('\n');

  return [
    `<h2 id="${joining.id}" data-spy>\n  ${joining.heading}\n</h2>`,
    intro,
    `<div class="pathway-grid">\n${cards}\n</div>`,
  ].filter(Boolean).join('\n\n');
}

function renderHome(dataPath = DEFAULT_PATH) {
  const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
  const sections = [data.about, data.workshop, data.joining];
  const index = sections.map((s) => ({ id: s.id, label: s.heading }));
  const body = [
    renderAbout(data.about),
    renderWorkshop(data.workshop),
    renderJoining(data.joining),
  ].join('\n\n') + '\n';
  return { body, index };
}

module.exports = { renderHome, renderFigure };
