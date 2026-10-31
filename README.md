# Dooservice locales

Every text Dooservice shows a person, in every language it speaks: the panel, the emails,
the console, the description of a pull request, the website. One place, so a language is
added once and reaches everything.

Code, comments, commits and a pull request's title stay in English and never come from
here. Only what is written for a person to read does.

## Layout

```
languages.json            the languages the platform offers: code, English name, own name
en/                       the reference: every other language has the same keys
  panel/<namespace>.json  the panel (app.dooservice.sh), one file per i18next namespace
  emails.json             the emails the orchestrator sends
  console.json            the console's welcome and splash
  pull-request.json       a published pull request's section headings and closing lines
  landing.json            dooservice.sh
  status.json             the page a server shows while an environment is down
es/ pt/ fr/ it/ de/        the same files, translated
```

A key a language lacks reads in English, and so does a whole file. Blanks keep the
syntax of the code that fills them: `{{name}}` in the panel (i18next), `{name}` everywhere
else.

## Adding a language

1. Add it to `languages.json`.
2. Copy `en/` to its two-letter code and translate the values; never the keys or the blanks.
3. `python3 tools/check.py --strict` passes when nothing is left in English.

## Changing a text

Change it in `en/` and in every language in the same pull request. The check refuses a key
English does not have and a blank that differs from English; it reports how many texts
still read in English.

## How it is used

Each repository that shows text takes this one as a git submodule and reads only its own
files at build time; nothing is fetched while running.

## License

Apache-2.0.
