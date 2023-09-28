import * as $ from 'jquery';
import { Slider, Sticky, Drilldown } from 'fdn/js/foundation';

import svgPersonFillin from '../svg/material-symbols-person.svg';
import svgResearchFillin from '../svg/material-symbols-function.svg';

export function initDarkModeToggle() {

  $( '#dark-mode-switch' ).on('change', function() {
    // when the toggle changes, update the html attribute to reflect the
    // current preference, which affects the rest of the page indirectly
    // through css
    const isDark = $( this ).prop('checked');
    $( 'html' ).attr('data-theme', (isDark) ? 'dark' : 'light');
  });

  // https://stackoverflow.com/a/57795495/1552418
  if (window.matchMedia) {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      // user prefers dark mode, so set dark mode
      $( '#dark-mode-switch' ).prop('checked', true);
      $( 'html' ).attr('data-theme', 'dark');
    } else {
      // user prefers light mode or has no preference set, so set light mode
      $( '#dark-mode-switch' ).prop('checked', false);
      $( 'html' ).attr('data-theme', 'light');
    }
  } else {
    // can't use matchmedia, so assume dark mode by default
    $( '#dark-mode-switch' ).prop('checked', true);
    $( 'html' ).attr('data-theme', 'dark');
  }
}

export default (function() {

  $( document ).ready(() => {

    // initialize page controls
    initDarkModeToggle();

    $( '.person-thumbnail:not([src])' )
      .attr('src', svgPersonFillin)
      .attr('data-fillin', '')
      .attr('aria-hidden', 'true');
    $( '.research-thumbnail:not([src])' )
      .attr('src', svgResearchFillin)
      .attr('data-fillin', '')
      .attr('aria-hidden', 'true');

    // putting this last may help with the "fouc" problem
    $( document ).foundation();
  });
})();

// vim: set ft=javascript:
