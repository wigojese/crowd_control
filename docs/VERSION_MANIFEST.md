# VERSION MANIFEST (Stage 07)

| Item | Pinned value | Where pinned | Label |
|---|---|---|---|
| Engine | Godot **4.7.2 stable** (18 Aug 2026), official Linux x86_64 build | `project.godot` `config/features`; `.github/workflows/ci.yml` | Version VERIFIED (Stage 06). **Never run in this project (BLOCKED)** |
| Download check | SHA-512 of `Godot_v4.7.2-stable_linux.x86_64.zip` against the release's `SHA512-SUMS.txt` | CI step; done once by hand in Stage 06 | VERIFIED once |
| Language | GDScript (provisional, CC-D-013) | | PROVISIONAL |
| Ruleset | CC-RULESET-01C | `data/events.schema.json`, `CcScenarioValidator.RULESET` | IMPLEMENTED/TESTED (validator, Python) |
| Python (tooling only) | 3.x, standard library only; run as `python3 -I` | `scripts/` | Run here with `/usr/local/bin/python3` |
| Fonts | Inter, Inter Display, JetBrains Mono, SIL OFL 1.1. No font files in the repo yet | `assets/fonts/licenses/` | Licence texts copied from the Debian packages' copyright files. Inter's file states "OFL-1.1 and Apache-2.0"; which files carry which licence is **UNVERIFIED** until the font files are added |
| Third-party code | none | | |
| Android target | API 36 required by Google Play from 31 Aug 2026 | Stage 06 sources | VERIFIED (read), not built |

Upgrade rule: no engine or version change without a new approval (spec E1).
