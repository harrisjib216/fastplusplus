# Contributing to fastpp

Thanks for helping keep the catalog accurate. Three kinds of contribution are most useful, and each has an issue
form:

- **[New entry](../../issues/new?template=new-entry.yml):** a library or tool with a published, numeric comparison
  against a common default.
- **[Wrong number or fact](../../issues/new?template=wrong-number.yml):** a quote, ratio, license, link or status
  that does not match its source.
- **[Retier request](../../issues/new?template=retier-request.yml):** evidence that an entry belongs in a higher or
  lower tier (a reproducible harness was published, a harness flaw was found, a paper became readable).

## What counts

An entry needs a numeric comparison against a recognisable baseline that developers use by default for the same
task, on a page anyone can open. Marketing pages count as tier C at best. A project with no comparison at all
belongs in [seeds without evidence](catalog/seeds-no-evidence.md), not in the catalog.

| Tier | Requirement |
|:-:|---|
| A | Public benchmark code, run against the named baseline, with compiler, flags and CPU model stated, whoever ran it. |
| B | An independent or peer-reviewed measurement that falls short of A. |
| C | First-party numbers without the full methodology. |
| D | Directional only, no numbers; kept for notable projects. |

Two rules shape every decision:

- **Keep and document.** Weak, first-party, off-baseline or not-faster evidence keeps the entry at a lower tier
  with the problem written down. Do not ask for removal because an entry is weak; ask for the shortcoming to be
  recorded.
- **Reject only invalid evidence**: a benchmark that times the wrong thing, hard-coded results, a fast path that
  computes a different answer, numbers that were never measured. Examples are in
  [rejected claims](catalog/rejected.md) and in [how it was built](docs/how-it-was-built.md).

## Pull requests

Files under `catalog/` and the generated blocks of `README.md` are rebuilt from `data/` and must not be edited by
hand. A data change goes in through the pipeline:

- **Shortcomings, duplicates and overrides** (name, category, domain, repo URL, language) are recorded with
  `pipeline/add_decisions.py`:

  ```sh
  python3 pipeline/add_decisions.py <<'EOF'
  {"id":"https://github.com/owner/repo","s":"shortcoming text, with the source","m":"who measured it"}
  EOF
  ```

- **Tier moves and corrected fields** go in a retier file,
  `data/waveN/verify/raw/retier-NN.json`, as `[{id, evidence_tier_final, tier_reason, corrections{...},
  urls_opened}]`, then `python3 pipeline/verify.py apply data/waveN`.
- **New entries** go through a search or seed record, verification and enrichment, as described in the wave loop
  in [CLAUDE.md](CLAUDE.md#the-wave-loop). Opening a new-entry issue is usually easier.

Before you open the pull request:

```sh
python3 pipeline/render_lists.py   # rebuild catalog/ and the README blocks
python3 pipeline/check_pii.py      # no home-directory paths, personal emails or credentials
```

CI runs both and fails if the committed catalog differs from a fresh render.

## Privacy

Do not commit personal names, personal email addresses, home-directory paths or credentials. Prompts rendered on
a personal machine embed the checkout's absolute path; `python3 pipeline/check_pii.py --fix` rewrites those
paths to `/path/to/fastpp`.

## License

By contributing you agree that your contribution is licensed under the [MIT License](LICENSE).
