#!/usr/bin/env bash
#
# Verify a webpack build produced every file the site needs.
#
# Shared by both workflows, deliberately: build-check.yaml used to check more
# than build-site.yaml did, which is backwards - the workflow that publishes
# should never validate less than the one that only gates a pull request.
# One script means the two cannot drift apart again.
#
# Usage: scripts/check_build_output.sh [--publish] [dist-dir]
#
#   --publish   also require the files added only on the publishing path
#               (CNAME, .nojekyll)
#
# Exits non-zero, after reporting every problem rather than only the first,
# if anything is missing or empty.

set -euo pipefail

publish=0
dist=dist

for arg in "$@"; do
  case "$arg" in
    --publish) publish=1 ;;
    -*) echo "unknown option: $arg" >&2; exit 2 ;;
    *) dist="$arg" ;;
  esac
done

fail=0

# ::error:: becomes an annotation in the Actions log and is harmless locally.
require() {
  if [ ! -s "$dist/$1" ]; then
    echo "::error::$dist/$1 is missing or empty"
    fail=1
  fi
}

# .nojekyll is a marker file and is legitimately zero bytes, so it is checked
# for existence rather than for content.
require_exists() {
  if [ ! -e "$dist/$1" ]; then
    echo "::error::$dist/$1 is missing"
    fail=1
  fi
}

for page in index people research 404; do
  require "$page.html"
done

for f in robots.txt sitemap.xml site.webmanifest favicon.ico favicon.svg; do
  require "$f"
done

if [ "$publish" -eq 1 ]; then
  require CNAME
  require_exists .nojekyll
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi

echo "All expected files built. ✓"
