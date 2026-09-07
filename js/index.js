/*
 * Three behaviours, no dependencies.
 *
 *   1. The theme switch: reflect the theme chosen before first paint by the
 *      inline script in <head>, write the user's choice to localStorage, and
 *      follow the OS while nothing is stored.
 *   2. Scrollspy: mark the section the reader is in, in both copies of the
 *      in-page index (the rail's and the narrow-width disclosure's).
 *   3. Reveal the rail mark once Home's hero has scrolled past, so the mark
 *      and the wash are never drawn on one screen.
 *
 * With JS off: the theme is whatever the inline script or the media query
 * settled on, the index is a plain list of working anchors, and the rail mark
 * is simply shown.
 */

const root = document.documentElement;
const STORE = 'theme';

/** localStorage throws in Safari's private mode; a theme is not worth a crash. */
function stored(value) {
  try {
    if (value === undefined) return window.localStorage.getItem(STORE);
    window.localStorage.setItem(STORE, value);
  } catch (e) { /* no storage: the choice lasts for this page only */ }
  return null;
}

// -------------------------------------------------------------------------
// 1. Theme
// -------------------------------------------------------------------------

function initTheme() {
  const dark = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  const isDark = () => root.getAttribute('data-theme') === 'dark';
  const switches = Array.prototype.slice.call(document.querySelectorAll('.switch'));
  // The two <meta name="theme-color"> tags are scoped by media query, which
  // browsers only re-evaluate against the OS. An explicit choice repaints both
  // with that theme's colour so the browser chrome follows the page.
  const metas = Array.prototype.slice.call(document.querySelectorAll('meta[name="theme-color"]'));
  const chrome = {};
  metas.forEach((m) => {
    chrome[/dark/.test(m.getAttribute('media') || '') ? 'dark' : 'light'] = m.getAttribute('content');
  });
  // True once the reader has used the switch on this page - the choice that
  // outranks the OS even when storage is unavailable to remember it.
  let explicit = false;

  function paint(theme) {
    root.setAttribute('data-theme', theme);
    switches.forEach((el) => el.setAttribute('aria-checked', String(theme === 'dark')));
    if (chrome[theme]) metas.forEach((m) => m.setAttribute('content', chrome[theme]));
  }

  // The inline head script has already set data-theme; this only catches the
  // switch up with it.
  paint(isDark() ? 'dark' : 'light');

  switches.forEach((el) => {
    el.addEventListener('click', () => {
      const next = isDark() ? 'light' : 'dark';
      explicit = true;
      paint(next);
      stored(next);
    });
  });

  // Follow the OS, but only while the reader has expressed no preference of
  // their own - an explicit choice outranks the system one.
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

  // How much of the top of the viewport the navigation covers. In rail mode the
  // rail is a column beside the content and covers nothing; once it collapses
  // into a bar it covers its own height, measured rather than assumed.
  const rail = document.querySelector('.rail');
  const isBar = window.matchMedia('(max-width: 47.99em)');
  const sticky = () => (isBar.matches && rail ? rail.getBoundingClientRect().height : 0);

  /*
   * A 1px probe line sits just below the sticky bar. The current section is
   * the last one whose top has crossed it; if none has - the reader is above
   * the first heading - it is the first section. Exactly one is current, and
   * the rule is ordered, so two adjacent sections can never both claim it.
   */
  function measure() {
    queued = false;
    // Just below where a fragment link parks its target, so following one from
    // the index marks the section it just landed on rather than the one above.
    const clearance = parseFloat(
      getComputedStyle(sections[0]).scrollMarginTop) || 0;
    const probe = Math.max(sticky(), clearance) + 4;
    let found = sections[0];
    for (let i = 0; i < sections.length; i += 1) {
      if (sections[i].getBoundingClientRect().top <= probe) found = sections[i];
    }
    // At the very bottom of the page the last section may never reach the
    // probe; if the page is scrolled to its end, it is what the reader sees.
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

// -------------------------------------------------------------------------
// 3. The rail mark on Home
// -------------------------------------------------------------------------

function initHeroMark() {
  const hero = document.querySelector('.hero');
  const mark = document.querySelector('.rail-mark');
  if (!hero || !mark || !('IntersectionObserver' in window)) return;

  // The class says what is true; the stylesheet decides what that costs - a
  // hidden box in the rail, no box at all in the bar.
  const rail = mark.parentNode;
  const show = (on) => rail.classList.toggle('hero-on', !on);
  show(false);
  new IntersectionObserver((entries) => {
    entries.forEach((entry) => show(!entry.isIntersecting));
  }, { threshold: 0 }).observe(hero);
}

initTheme();
initScrollspy();
initHeroMark();

// vim: set ft=javascript:
