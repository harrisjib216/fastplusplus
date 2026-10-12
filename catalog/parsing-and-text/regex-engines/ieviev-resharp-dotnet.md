# RE# (Resharp)

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Regex engines](README.md)</sub>

**Tier B** (independent or peer-reviewed measurement) · Copyable · `F#` · `MIT` · 🟢 active

> Automata-based .NET/F# regex engine beating Rust's regex crate on rebar benchmarks; adds intersection, complement, lookarounds.

| | |
|---|---|
| **Beats** | Rust regex |
| **Claimed result** | Paper (arXiv 2407.20479) states RE# places first overall on the rebar baseline suite (27 supported benchmarks), 'over 71% faster than the next fastest engine Rust' (geometric-mean slowdown 1.48 vs 2.54; the paper itself gives 2.54/1.48 = 1.716). On the extended benchmarks (Fig. 5b) RE# is first overall (1.09 vs Hyperscan 3.77, rust/regex 29.5), 'often by several orders of magnitude'. RE# is not fastest in every category: rust/regex has lower slowdown in baseline categories 6.1.1 literal/literal-alternate (1.49 vs 1.98) and 6.1.3 (1.38 vs 1.43). Repo README separately shows RE# 37x-34,833x faster than .NET Compiled/SourceGenerated on curated rebar patterns. |
| **Workload** | BurntSushi/rebar benchmark suite: finding all matches for baseline categories (literal, words, bounded-repeat, ReDoS, quadratic, date/dictionary) plus extended categories (monster regexes, character sets, Unicode, lookarounds), comparing against Rust regex, RE2, PCRE2, and Hyperscan |
| **Metric** | throughput |
| **Hardware** | Paper: AMD Ryzen Threadripper 3960X 24-Core, 128 GB RAM, Ubuntu 22.04 Docker image (Sec. 6). README table: AMD Ryzen 7 5800X, .NET 10.0 |
| **Adoption** | 257 stars |
| **Last commit** | 2026-07-04 |
| **Links** | [repository](https://github.com/ieviev/resharp-dotnet) · [benchmark](https://arxiv.org/abs/2407.20479) |

## Verdict

Per the peer-reviewed paper (arXiv 2407.20479), on BurntSushi/rebar's 27-benchmark baseline suite RE# posts a geometric-mean slowdown of 1.48 vs Rust regex's 2.54 (paper's own '71% faster' framing), and on extended benchmarks RE# is 1.09 vs Hyperscan 3.77 and rust/regex 29.5, measured on an AMD Threadripper 3960X 24-core/128GB RAM Ubuntu 22.04 Docker box with engine versions and compiler/runtime flags unstated. The repo's own README table separately shows RE# 37x-34,833x faster than .NET's Compiled/SourceGenerated regex on curated rebar-derived patterns (Ryzen 7 5800X, .NET 10.0).

## Use it when

- Large/complex patterns (many alternations, loops, big Unicode classes) where .NET's Compiled/SourceGenerated engines and Rust regex both degrade
- Untrusted input where guaranteed non-backtracking, linear-time matching is needed to rule out ReDoS
- Patterns needing lookaround in a non-backtracking automata engine, or boolean composition of constraints (e.g. 'matches A and matches B and length in range') via intersection/complement
- Same compiled pattern reused many times over large .NET/F# text buffers, using `ValueMatches` for zero-allocation matching
- .NET/F# codebases already comfortable adding a NuGet dependency for a non-standard regex type

## Skip it when

- Non-.NET stacks — ships only as a .NET library; the companion Rust rewrite (github.com/ieviev/resharp) is, per its author, currently slower than this F# version
- Need multi-group capture extraction — RE# has no capturing groups beyond the whole match (\$0 only in Replace); pair with another engine for group extraction
- Need lazy quantifiers, backreferences, balancing groups, or conditional patterns — unsupported, automata-only feature set
- Need PCRE/.NET leftmost-first semantics — RE# is leftmost-longest, which changed match results on 2 of 27 rebar baseline benchmarks vs. leftmost-greedy engines
- Simple literal or literal-alternation patterns — the paper shows Rust regex has a lower slowdown than RE# in exactly these two baseline categories

## How it is fast

Patterns compile ahead of time into a symbolic (minterm-partitioned) automaton: the alphabet is collapsed into equivalence classes via a BDD-backed solver (BitVector/UInt64/CharSet solvers) so transition tables stay small regardless of Unicode range. Matching is derivative-based, non-backtracking, and guaranteed linear-time; RE# optionally precompiles a full DFA up front (`ResharpOptions.HighThroughputDefaults`, `DfaThreshold`) or falls back to lazy on-the-fly DFA construction for very large patterns, plus start-set inference and literal-prefix scanning to skip non-matching regions.

## Compared with alternatives

Locked into .NET/F# and need Rust-regex-beating throughput plus features Rust's regex crate can't do at all (intersection, complement, lookarounds); coregex is the only other sibling benchmarked against Rust regex, but it's a different (non-.NET) engine and wins on fewer patterns (6 of 16) rather than topping an independent multi-engine suite the way RE# does on rebar.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none |
| **Minimum toolchain** | .NET SDK 8+ (multi-targets net8.0;net9.0;net10.0), F# compiler for the core library |
| **Platforms** | any (managed .NET/F#; no native code or SIMD intrinsics documented) |
| **Thread safety** | A Regex instance is thread-safe and shareable across threads without external locking; matching methods lock internally only during DFA construction, then run lock-free once the state graph is built (docs/api.md) |
| **Drop-in for the baseline** | partial — explain: same broad method shapes as System.Text.RegularExpressions (IsMatch/Matches/Count/Replace) but a different type, extended (&, \~, _) syntax, no capture groups beyond \$0, and leftmost-longest instead of leftmost-first semantics |

## Gotchas

- `ValueMatches` returns a disposable pooled value list — must be `use`/disposed or pooled memory leaks
- Leftmost-longest matching can return a different match than .NET's or PCRE's leftmost-first engines for the same pattern
- Lookarounds cannot be nested, unioned across alternatives, or placed mid-pattern — only at pattern edges (confirmed by closed issue #2 on this exact limitation)
- No numbered capture groups; `Replace` supports `$0` only, so multi-group extraction needs a second pass with a different engine

## Caveats and trade-offs

The paper omits engine version numbers ('most recent available stable versions') and gives no compiler/runtime flags, so tier stays B. Rust regex still wins the literal/literal-alternate category. RE# uses leftmost-longest semantics: 2 of 27 baseline benchmarks gave different match results than leftmost-greedy engines, and benchmarks that need capture groups were excluded. The README's own table compares RE# only against .NET's built-in engines.

.NET/F# only (companion from-scratch Rust reimplementation exists at github.com/ieviev/resharp but author says it is currently slower than the F# version); extends regex syntax with intersection (&), complement (\~(...)), and universal wildcard (_) beyond standard .NET regex; uses leftmost-longest match semantics, not PCRE-style leftmost-first

## Maintenance

Active (last commit 2026-07-04), MIT-licensed and published on NuGet as `Resharp`; 257 stars puts it early-stage rather than widely adopted, but it's a small managed library with no external dependencies, so it's cheap to vendor or pin.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification B, tier now B.
- **Tier reason:** Peer-reviewed paper (arXiv 2407.20479) evaluated with the independent BurntSushi/rebar suite; Fig. 5a shows geometric-mean slowdown RE# 1.48 vs rust/regex 2.54. CPU is stated (Threadripper 3960X), but engine versions and compiler/runtime flags are omitted, so not A.
- **Verifier notes:** Opened the arXiv PDF: the 71% figure and the 2.54/1.48 ratio are stated in the paper itself, so the 'derived from page data' label was removed. Venue POPL 2025 comes from the README's DOI link (10.1145/3704837), which I did not open. Metadata (MIT, 257 stars, last commit 2026-07-04) verified.
- **Fields the verifier corrected:** `claimed_speedup`, `hardware`, `caveats`
- **Pages the verifier opened:**
  - <https://arxiv.org/abs/2407.20479>
  - <https://arxiv.org/pdf/2407.20479>
  - <https://github.com/ieviev/resharp-dotnet>
- **Sources the enricher read:**
  - <https://github.com/ieviev/resharp-dotnet>
  - <https://github.com/ieviev/resharp-dotnet/blob/main/README.md>
  - <https://github.com/ieviev/resharp-dotnet/blob/main/docs/api.md>
  - <https://github.com/ieviev/resharp-dotnet/blob/main/docs/syntax.md>
  - <https://github.com/ieviev/resharp-dotnet/blob/main/Directory.Build.props>
  - <https://github.com/ieviev/resharp-dotnet/blob/main/src/Resharp/Resharp.fsproj>
  - <https://github.com/ieviev/resharp-dotnet/issues>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/ieviev/resharp-dotnet`) · [data/wave3/enrich/raw/github_com_ieviev_resharp_dotnet.json](../../../data/wave3/enrich/raw/github_com_ieviev_resharp_dotnet.json) (enrichment confidence 0.72)

</details>
