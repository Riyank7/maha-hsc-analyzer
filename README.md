# Maharashtra HSC Paper Analyzer

A local, static evidence viewer for main English-medium Class XII papers in the 2007–2026 research window. Subjects: Physics, Chemistry, Arts & Science Mathematics, English, bifocal Computer Science I and II theory.

## Open locally

From this directory run `python3 -m http.server 8765 --bind 127.0.0.1`, then open <http://127.0.0.1:8765/>. No build or external API is required. The existing preview runs on this port.

## Current coverage

107 distinct usable PDFs; 94 question / question-block reviews and 13 older English section reviews. All five recent years (2022–2026) have all six paper types. Historical coverage is incomplete. See `reports/analysis.html` and `data/coverage.json` for gaps, including Mathematics 2012 Paper II. 2021's cancelled main exam is excluded.

The four original failed 2025 PCM / English downloads were recovered, as were 2015–2016 CS copies. All 15 previously failed subject/year entries now have local replacements, including seven older CS papers assembled from complete public scan pages; see `data/download-recovery.json`. Incomplete and mislabeled copies remain only in the audit trail.

## Data and methodology

- `data/papers.json`: full source audit index, local paths, SHA-256 hashes, duplicate and exclusion flags. Display only rows without `duplicateOf` or `excluded`.
- `data/questions.json`: reviewed questions / blocks. Older English entries use `marksBasis: required-section`; do not combine them with offered chapter marks.
- `data/english-sections.json`: required English section allocations for historical comparison.
- `data/chapters.json`: generated 20 / 10 / 5 year aggregates.
- `sources/`: original downloaded PDFs, cached source pages, extracted text and OCR. Not all cached attempts are usable PDFs.
- `scripts/reviewed.py`: reviewed mappings and total reconciliation.
- `stats.js`: shared browser / report aggregation. Equal weight per year, pre-2013 parts combined within year, mixed blocks retained without inventing subpart allocations. Individual upper bounds overlap and must not be summed.

Offered marks include mutually exclusive alternatives, and exceed a student's attainable marks. English historical section comparisons use required marks instead. Older undated retyped PCM dates follow archive attribution. This is not a complete set of every regional paper variant or a prediction of future weightage.

## Regenerate reviewed data and report

Run `python3 scripts/reviewed.py`, followed by `node scripts/build_report.cjs`. These use the standard libraries only. Downloads / extraction additionally need `pypdf`, and image-based PDF assembly needs Pillow. `scripts/ocr.swift` uses macOS Vision / PDFKit for offline OCR. The local `.hsc-python` symlink points to this machine's bundled runtime and is not portable.

`collect.py` is the original collection pass and rewrites its output index; do not rerun it over the curated index without backing it up. Use recovery manifests plus `scripts/curate.py` to merge newly downloaded papers safely. `parse_halves.py` is exploratory only; its output is not accepted as reviewed evidence.

The base app can be served by any static server. For Cloudflare Pages, build with `python3 scripts/build_site.py` and deploy `dist/` using Wrangler. The Google sign-in feature is developed separately in a pull request; it requires Pages Functions and Google OAuth configuration before activation.
