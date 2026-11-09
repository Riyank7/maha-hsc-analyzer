# Maharashtra HSC Paper Analyzer

A local, static evidence viewer for main English-medium Class XII papers in the 2007–2026 research window. Subjects: Physics, Chemistry, Arts & Science Mathematics, English, bifocal Computer Science I and II theory.

## Google sign-in feature

Required Google sign-in is active through Cloudflare Pages Functions using the dedicated personal Google project. [Configuration and recovery instructions](docs/GOOGLE_SIGN_IN.md) describe the setup. The implementation was merged in [PR #1](https://github.com/Riyank7/maha-hsc-analyzer/pull/1). Live Google sign-in has been tested. Use `npm ci`, `npm test`, and `npm run dev` for the authenticated app. Unconfigured authentication fails closed.

## Open locally (static base only)

From this directory run `python3 -m http.server 8765 --bind 127.0.0.1`, then open <http://127.0.0.1:8765/>. This static preview does not enforce the Google sign-in added by the feature branch. The existing preview runs on this port.

## Current coverage

111 distinct usable PDFs; 98 question / question-block reviews and 13 older English section reviews. All five recent years (2022–2026) have all six paper types. Historical coverage is incomplete. See `reports/analysis.html` and `data/coverage.json` for gaps, including Mathematics 2012 Paper II. 2021's cancelled main exam is excluded.

The four original failed 2025 PCM / English downloads were recovered, as were 2015–2016 CS copies. All 15 previously failed subject/year entries now have local replacements, including seven older CS papers assembled from complete public scan pages; see `data/download-recovery.json`. Incomplete and mislabeled copies remain only in the audit trail.

## Data and methodology

The Exam dates tab shows the six subjects in this app for the February–March
2027 written examinations, with fixed IST times and page-specific source links.
The original user-supplied 12-page Board timetable is preserved unchanged under
sources/timetables/. Its hash and the reviewed entries are recorded in
data/timetable-2027.json. The build verifies the hash before packaging the PDF.
The timetable and document use the existing required Google sign-in.

The latest recovery added the four 2011 Physics/Chemistry parts and replaced
2011/2013 English with clearer complete scans. [Recovery audit and remaining
gaps](docs/PAPER_RECOVERY.md) records rejected session labels and access limits.

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

The base app can be served by any static server. For Cloudflare Pages, build with `python3 scripts/build_site.py` and deploy `dist/` using Wrangler. The merged Google sign-in implementation uses Pages Functions and requires Google OAuth configuration.

## Automatic deployments

GitHub Actions tests authentication, validates all paper files and marks, builds the site, and compiles its Worker on pull requests. Pushes and merges to `main` then deploy to <https://maha-hsc-analyzer.pages.dev> and verify that anonymous data/PDF requests remain blocked. The workflow can also be run manually from Actions.

Required repository configuration: encrypted Actions secret `CLOUDFLARE_API_TOKEN` (dedicated Pages Edit token), and Actions variable `CLOUDFLARE_ACCOUNT_ID`. These are deployment credentials, separate from the Google client secrets stored only in Cloudflare. The token must be rotated before its expiry.

Each build emits public, non-sensitive version metadata. Open analyzer and login pages check it every 15 seconds and reload when a new build appears. The analyzer preserves the selected tab, subject, year, and analysis period across that refresh. No login tokens are stored in browser storage.

## Locked answer library

The Answers tab requires the shared password after Google sign-in. The password is not in the repository. The edge verifies a salted PBKDF2 hash and issues a two-hour HttpOnly unlock cookie tied to the Google user. Answer files are AES-256-GCM encrypted before committing; the decryption key and password verifier are encrypted Cloudflare secrets. Plaintext drafts and the local credential file remain under ignored private/. Public publisher solutions are linked with attribution and remain public on their own sites.

See [answer-library maintenance](docs/ANSWERS.md). The locked catalog reports published references, original worked answers and remaining preparation separately.

Current collected-corpus coverage: 68 published solution-reference sets and 43
original worked-answer sets, with no sets still in preparation. Original sets
contain 1,213 grouped question/subquestion answers. All are study resources, not
official marking schemes; uncertainties and source defects are labelled.
