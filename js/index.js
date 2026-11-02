/*
 * Client-side behaviours (zero dependencies):
 *
 *   1. Theme switch: synchronize with the theme chosen before first paint by
 *      the inline script in <head>, persist explicit user choices to
 *      localStorage, and follow OS preference changes when nothing is stored.
 *   2. Scrollspy: highlight the active section in both copies of the in-page
 *      index (the desktop sidebar rail and the narrow-width disclosure).
 */

const root = document.documentElement;
const STORE = 'theme';

function stored(value) {
  try {
    if (value === undefined) return window.localStorage.getItem(STORE);
    window.localStorage.setItem(STORE, value);
  } catch (e) { /* storage unavailable (e.g. private browsing) */ }
  return null;
}

// -------------------------------------------------------------------------
// 1. Theme
// -------------------------------------------------------------------------

function initTheme() {
  const dark = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const isDark = () => root.getAttribute('data-theme') === 'dark';
  const switches = Array.prototype.slice.call(document.querySelectorAll('.switch'));
  const metas = Array.prototype.slice.call(document.querySelectorAll('meta[name="theme-color"]'));
  const chrome = {};
  metas.forEach((m) => {
    chrome[/dark/.test(m.getAttribute('media') || '') ? 'dark' : 'light'] = m.getAttribute('content');
  });
  let explicit = false;

  function paint(theme) {
    root.setAttribute('data-theme', theme);
    switches.forEach((el) => el.setAttribute('aria-checked', String(theme === 'dark')));
    if (chrome[theme]) metas.forEach((m) => m.setAttribute('content', chrome[theme]));
  }

  paint(isDark() ? 'dark' : 'light');

  switches.forEach((el) => {
    el.addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark';
      explicit = true;
      paint(next);
      stored(next);
    });
  });

  if (dark && dark.addEventListener) {
    dark.addEventListener('change', (e) => {
      if (!explicit && stored() === null) paint(e.matches ? 'dark' : 'light');
    });
  }
}

// -------------------------------------------------------------------------
// 2. Scrollspy
// -------------------------------------------------------------------------

function initScrollspy() {
  const sections = Array.prototype.slice.call(document.querySelectorAll('[data-spy]'));
  const links = Array.prototype.slice.call(document.querySelectorAll('[data-spy-for]'));
  if (!sections.length || !links.length) return;

  let current = null;
  let queued = false;

  const rail = document.querySelector('.rail');
  const isBar = window.matchMedia ? window.matchMedia('(max-width: 47.99em)') : null;
  const sticky = () => (isBar && isBar.matches && rail ? rail.getBoundingClientRect().height : 0);

  function measure() {
    queued = false;
    const clearance = parseFloat(
      getComputedStyle(sections[0]).scrollMarginTop) || 0;
    const probe = Math.max(sticky(), clearance) + 4;
    let found = sections[0];
    for (let i = 0; i < sections.length; i += 1) {
      if (sections[i].getBoundingClientRect().top <= probe) found = sections[i];
    }
    if (document.body.scrollHeight > window.innerHeight
        && window.innerHeight + window.scrollY >= document.body.scrollHeight - 2) {
      found = sections[sections.length - 1];
    }
    if (found.id === current) return;
    current = found.id;

    links.forEach((link) => {
      const on = link.getAttribute('data-spy-for') === current;
      if (on) {
        link.setAttribute('aria-current', 'true');
      } else {
        link.removeAttribute('aria-current');
      }
    });
  }

  function schedule() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(measure);
  }

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  measure();
}

initTheme();
initScrollspy();
