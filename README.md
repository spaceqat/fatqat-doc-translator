# FatQat translated documentation

This repository translates documentation from `spaceqat/fatqat` into Simplified
Chinese and Korean. Both editions use the same pinned English source and preserve
executable examples, API identifiers, generated docstrings, and plot labels.
English sources stay upstream.

Translations live in `translations/` as segment records (`id`, `en`, `zh`, `status`).
Korean records live in `translations-ko/` with `ko` in place of `zh`.
The extractor reuses unchanged translations. New English text becomes `pending`;
Codex fills the Chinese text and marks it `machine`. Only a human marks an entry
`reviewed`. Missing translations remain English in local previews.

## Build and validate

Use a dedicated Python 3.12+ virtual environment:

```sh
python -m pip install -r requirements.txt
python tools/translate.py check
python -m unittest discover -s tests -v
python tools/inject_build.py --output site
```

Chinese remains the default. For Korean, select the locale explicitly:

```sh
python tools/translate.py --locale ko extract
python tools/translate.py --locale ko check --require-complete
python tools/inject_build.py --locale ko --output site-ko --require-complete
```

After syncing upstream, extract and complete both databases. Each locale has its
own style guide and glossary. Review technical meaning, protected syntax, and
natural prose in separate passes; machine-assisted review never changes a record
to `reviewed`. Rendered output belongs in ignored build directories, not Git.
See `ONBOARDING.md` for Korean hosting setup.

The build clones the upstream commit in `UPSTREAM_COMMIT`, verifies its source
snapshot, builds upstream assets and executable tutorials, then renders and
builds the selected language. It reuses tutorial caches on repeated local builds.
Add `--require-complete` to reject untranslated segments before publishing.
No translation service is called during an RTD build.

Read the Docs runs preparation/dependency installation, tutorial execution,
English asset generation, and the translated site as separate commands using
`--stage prepare`, `--stage tutorials`, `--stage english`, and
`--stage translated`, in that order. They share the same `--workdir` and locale.
Local builds still run all stages by default. This keeps the completed stages'
logs available if a later stage is killed; RTD saves command output on completion.
It does not increase RTD's build time or memory limits. An inactivity notification
alone does not identify a Python error: inspect the completed commands and the
project's build notifications before diagnosing the failure.

Translated headings preserve their English anchors. Navigation and tutorial
categories are generated from the pinned source and use the same segment database.
Examples remain executable and unchanged. Generated Python API docstrings and
plot labels currently remain English.
Every translated page includes an LLM translation notice in its footer,
with a link to this repository's GitHub Issues for translation feedback.

## Sources and versions

- `upstream.yml`: canonical repository, main ref, release-tag pattern, English URL.
- `UPSTREAM_REF` / `UPSTREAM_COMMIT`: exact source version for this branch.
- `upstream-docs/`: machine-managed snapshot; update with `tools/sync_upstream.py`.
- `translations/`: authored translation database and terminology/style rules.
- `translations-ko/`: Korean database, terminology, and style rules.
- `tools/`: extraction, validation, rendering, and build tools.
- `overlay/mkdocs.zh.yml`: minimal Chinese theme settings; navigation is generated.
- `overlay/mkdocs.ko.yml`: Korean theme and search settings.
- `overlay/assets/`: translated typography adjustments; homepage structure and assets
  continue to use the pinned upstream templates.

`main` is the latest documentation. Release branches use the upstream release
name and keep a separate source pin and translations. Read the Docs handles the
language/version URLs; each language is built directly at its version root.

See [ONBOARDING.md](ONBOARDING.md) for RTD configuration, version handling, and the
subscription-based scheduling proposal. The legacy GitHub sync workflow has been
removed. Recurring execution and automatic publication are not enabled.
