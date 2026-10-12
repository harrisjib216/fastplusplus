# nanoregex

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Pure-Zig regex engine beating Python's re module on 6 of 7 README benchmark patterns.

| | |
|---|---|
| **Beats** | Python re (CPython built-in re module) |
| **Claimed result** | 1.65x-2.8x faster than Python re on 6 of the 7 patterns in the README table (Python re is 1.5x faster on `fn [A-Za-z]+\(.*alloc`); the README text claims '8 of 8 head-to-head non-anchored patterns won', which contradicts its own 7-row table. Separately \~5000x faster than zig-regex 0.1.1 on a catastrophic-backtracking pattern (43 s -&gt; 8 ms), and a zigrep --regex query went from 43 s to 0.43 s end-to-end after switching engines. |
| **Workload** | Regex findAll over a 142 KB Zig source file, 200 iterations, ReleaseFast build; 7 patterns in the README table (pure literal, literal-prefix, `fn [A-Za-z]+\(.*alloc`, \d+, [a-z]+, alternation foo\|bar\|baz, IPv4-like) vs Python's re module; plus a catastrophic-backtracking pattern vs predecessor zig-regex 0.1.1. |
| **Metric** | throughput |
| **Compiler and flags** | zig build -Doptimize=ReleaseFast |
| **Adoption** | 2 stars |
| **Last commit** | 2026-06-23 |
| **Links** | [repository](https://github.com/justrach/nanoregex) · [benchmark](https://github.com/justrach/nanoregex/blob/main/README.md) |

## Verdict

First-party README table: findAll over a 142 KB Zig source file, 200 iterations, zig build -Doptimize=ReleaseFast, compared against Python's built-in re module (no CPU model given, no published comparison harness for the Python/zig-regex side). nanoregex wins 6 of 7 listed patterns by 1.65x-2.8x; Python re wins the `fn [A-Za-z]+\(.*alloc` pattern by 1.5x. Separately, \~5000x faster than predecessor zig-regex 0.1.1 on a catastrophic-backtracking pattern (43s to 8ms).

## Use it when

- Zig codebase wanting a dependency-free regex engine (no FFI, no libc regex, no PCRE binding)
- Workloads dominated by findAll over literal or literal-prefixed patterns (memmem/DFA fast paths)
- Migrating off zig-regex 0.1.1, especially away from patterns that risk catastrophic backtracking
- Zig 0.16.0+ toolchain, ReleaseFast builds where the lazy-DFA warmup cost is amortized over many calls

## Skip it when

- Need lookaround, named groups, in-pattern backreferences, inline flag groups, or Unicode property classes -- not supported, may silently diverge
- Patterns dominated by backtracking-only constructs where the Pike-VM fallback is the only correct path (loses the speed advantage)
- Non-Zig codebases -- no C ABI or bindings documented
- Need a widely-used/audited engine: 2 stars, single maintainer, no CI or fuzzing evidence found
- Correctness-critical Unicode text -- parity is only checked against Python re on 27 ASCII-oriented fixtures

## How it is fast

Dispatches each pattern to the cheapest of five tiers: memmem for pure literals, prefilter-plus-DFA for literal-prefixed patterns, a lazy subset-construction DFA for anchor/backref-free patterns under a 4096-state budget, and a Pike VM (linear-time, always correct) fallback otherwise. The DFA folds bytes into minterm classes (e.g. `[a-z]+` collapses 256 bytes to 2 classes), shrinking each transition-table row from 1 KB to 8 bytes so it fits in L1 cache.

## Compared with alternatives

All catalogued siblings (nim-regex, rejit, SafeRE, BLARE, RE#, coregex, re2jit) target PCRE2/RE2/JDK/.NET/Rust regex in C/C++/Rust/.NET ecosystems; nanoregex is the only Zig-native option, so pick it specifically when the project is already Zig and needs zero FFI, not for raw throughput versus those more mature engines.

## Integration

| | |
|---|---|
| **Form** | source-drop |
| **Dependencies** | none |
| **Minimum toolchain** | Zig 0.16.0 (from build.zig.zon minimum_zig_version) |
| **Platforms** | not documented (pure Zig, no arch-specific code observed; no CI config found in repo tree) |
| **Thread safety** | not documented -- Regex is mutable/stateful (lazy DFA fills its table on use), so likely not safe to share one instance across threads without external locking |
| **Drop-in for the baseline** | partial -- explain: drop-in replacement target is zig-regex 0.1.1, not Python re; API mirrors zig-regex closely enough that README says most callers switch by changing one build.zig path |

## Gotchas

- Methods take \*Regex (mutable), not \*const Regex -- the lazy DFA mutates internal state on first use, so a fresh Regex's first findAll call is slower (cache warmup) than subsequent calls
- DFA eligibility silently falls back to Pike VM for capture groups, anchors, lazy quantifiers, case-insensitive patterns, or patterns whose DFA would exceed 4096 states -- no user-visible signal of which path ran
- Patterns using unsupported syntax (lookaround, named groups, in-pattern backrefs) parse without error but matching may diverge from expectation
- README's own header claims '8 of 8 head-to-head non-anchored patterns won' but the table beneath it has 7 rows with 1 Python win -- read the table, not the prose

## Caveats and trade-offs

First-party README benchmark: no CPU model, and only the nanoregex side of the harness (src/bench.zig) is published; the script that timed Python re and zig-regex is not in the repo. README says '8 of 8' patterns won but its table has 7 rows with 1 loss. The \~5000x figure is vs zig-regex 0.1.1 (niche predecessor, backtracking engine), not a named category baseline; the relevant comparison is 1.65x-2.8x vs Python re (widely used, not on the named-baseline list). Very small/new project (2 stars), kept per the DO-NOT-EXCLUDE-ON-SIZE rule.

Pure Zig, no FFI/dependencies; dispatches between a literal memmem fast path, a lazy subset-construction DFA (byte-minterm compressed), and a Pike-VM fallback for correctness. Does not yet support lookaround, named groups, in-pattern backreferences, or Unicode property classes -- those fall back or diverge from a richer engine.

## Maintenance

Active (last commit 2026-06-23), MIT-licensed, single small source-drop (3,200 lines) -- easy to vendor and audit given no dependencies, but very new/unstarred (2 stars) with no CI evidence found in the repo tree.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README table vs Python re (per-pattern ms, 142 KB file, 200 iters, ReleaseFast); no CPU model stated and the Python-side comparison script is not in the repo (src/bench.zig only times nanoregex), so not A.
- **Verifier notes:** README numbers verified; record miscounted the table (said 7 of 8 wins, table shows 6 of 7) and the README's own '8 of 8' line is inconsistent. Metadata (MIT, 2 stars, last commit 2026-06-23, not fork/archived) matches gh.
- **Fields the verifier corrected:** `claimed_speedup`, `workload`, `caveats`
- **Pages the verifier opened:**
  - <https://github.com/justrach/nanoregex>
  - <https://github.com/justrach/nanoregex/blob/main/README.md>
  - <https://github.com/justrach/nanoregex/blob/main/src/bench.zig>
- **Sources the enricher read:**
  - <https://github.com/justrach/nanoregex>
  - <https://github.com/justrach/nanoregex/blob/main/README.md>
  - <https://github.com/justrach/nanoregex/blob/main/src/bench.zig>
  - <https://github.com/justrach/nanoregex/blob/main/build.zig.zon>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/justrach/nanoregex`) · [data/wave3/enrich/raw/github_com_justrach_nanoregex.json](../../../data/wave3/enrich/raw/github_com_justrach_nanoregex.json) (enrichment confidence 0.4)

</details>
