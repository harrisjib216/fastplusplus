# encoding_rs

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Parsing and text](../README.md) › [Unicode and UTF-8](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `(Apache-2.0 OR MIT) AND BSD-3-Clause` · 🟢 active

> Rust implementation of the WHATWG Encoding Standard; beats ICU at UTF-8/UTF-16/legacy transcoding on Web-shaped text.

| | |
|---|---|
| **Beats** | ICU |
| **Claimed result** | 7.23x faster decode and 7.00x faster encode than ICU for English UTF-8&lt;-&gt;UTF-16; 1.6x-3.9x faster for most other languages; some cases (UTF-16LE/BE) 0.30x-0.32x (slower than ICU) |
| **Workload** | Decoding/encoding real-world text samples in many languages (English, CJK, Arabic, etc.) between UTF-8/UTF-16/legacy encodings, x86_64 Haswell with SSE2, ICU 55 as shipped by Ubuntu 16.04 |
| **Metric** | throughput |
| **Hardware** | x86_64 (Haswell); also tested on ARMv7/ARMv8 (Raspberry Pi 3) |
| **Compiler and flags** | Rust, tested with and without explicit SSE2 enabled |
| **Adoption** | 467 stars; core dependency of Firefox/Gecko and Servo (WHATWG Encoding Standard implementation) |
| **Last commit** | 2026-09-24 |
| **Links** | [repository](https://github.com/hsivonen/encoding_rs) · [benchmark](https://hsivonen.fi/encoding-perf-2016-11/) |

## Verdict

Author's own 2016 benchmark measured encoding_rs against ICU 55 (as built by Ubuntu 16.04) on x86_64 Haswell, with and without explicit SSE2: English UTF-8&lt;-&gt;UTF-16 conversion was 7.23x faster decode and 7.00x faster encode than ICU, most other tested languages' UTF-8 conversions were 1.6x-3.9x faster, but UTF-16LE/UTF-16BE conversions were 0.30x-0.32x of ICU's speed (slower).

## Use it when

- Parsing arbitrary Web content (HTML/CSS/XML) whose declared or sniffed charset may be a legacy encoding, mirroring what a browser does
- UTF-8&lt;-&gt;UTF-16 conversion in a Gecko/Servo-like pipeline where FFI-friendly, allocation-free (Cow) conversion matters
- Targeting x86_64, aarch64, i686, or thumbv7neon where the `simd-accel` feature's runtime dispatch pays off
- no_std / no-allocator embedded contexts (crate supports no_std with `alloc` feature togglable)
- You want a small, vendorable crate (only WHATWG's \~40 encodings) rather than all of ICU's converters

## Skip it when

- You need ICU's full arbitrary-encoding converter surface (charsets outside the Web Encoding Standard) or ICU-specific APIs (transliteration, locale-aware behavior)
- You need UTF-16LE/UTF-16BE-labeled output specifically: those labels' "output encoding" is UTF-8 per spec, a documented API surprise, not a bug
- Encoding legacy CJK (Big5/GB/Shift_JIS/EUC-KR/Hanja/Hangul) at top speed by default: those encode paths are size-optimized, not speed-optimized, unless you opt into the `fast-*` Cargo features
- You need the full SIMD acceleration path on stable Rust without qualification: `simd-accel` depends on nightly-only features (`rustversion`, `any_all_workaround` crates), so a stable build may miss it
- Deciding based on the cited benchmark: it is a decade-old first-party 2016 post against ICU 55, and the library's own code has changed materially since (2018 and 2026 rewrites) per the README

## How it is fast

Non-streaming UTF-8 paths borrow (Cow) instead of copying when input is already valid, and UTF-8 validation itself uses the SIMD-accelerated simdutf8 crate. ASCII-heavy fast paths are hand-written and, with the `simd-accel` feature, runtime-multiversioned per target (AVX2+BMI1 detection via `multiversion`/`core_detect` on x86_64, NEON on aarch64/thumbv7neon) so a single binary picks the best code path at runtime. The README notes the ASCII acceleration was rewritten in 2026 for Zen 3/M3 Pro/Raspberry Pi 4, i.e. the code measured in the 2016 benchmark is not the code shipping today.

## Compared with alternatives

The catalogued siblings are narrower single-purpose primitives (UTF-8 validation: simdutf8, xutf, SimdUnicode, utf8_range, Parabix; normalization: Boost.Text, unicode-transforms; URL/IDNA: ada-url/idna); pick encoding_rs when the job is full transcoding between UTF-8/UTF-16 and arbitrary legacy Web charsets (e.g. sniffing and decoding real-world HTML), and pick one of the UTF-8-only validators instead when all you need is to validate or count code points in already-UTF-8 data.

## Integration

| | |
|---|---|
| **Form** | crate |
| **Dependencies** | cfg-if, scopeguard, multiversion_no_op (always); optional: multiversion (x86/x86_64 without baseline AVX2+BMI1), simdutf8 (x86/x86_64/aarch64/wasm32+simd128), core_detect (x86/x86_64), serde, rustversion + any_all_workaround (simd-accel feature) |
| **Minimum toolchain** | Rust 1.88 (MSRV, per Cargo.toml `rust-version`); `simd-accel` feature further constrains to Rust versions with the nightly features it needs |
| **Platforms** | any (falls back to portable code); SIMD acceleration tuned for x86_64, aarch64, i686, thumbv7neon via the `simd-accel` feature |
| **Thread safety** | not documented explicitly; `Encoding` values are `'static` references usable freely, but README/API docs give no explicit Sync/Send guarantee for `Decoder`/`Encoder` instances |
| **Drop-in for the baseline** | partial — replaces ICU's charset-conversion role for Web-defined encodings but exposes a different, Rust-native API (Decoder/Encoder streaming model) and does not cover ICU's full encoding catalog |

## Gotchas

- Encoding to UTF-16LE, UTF-16BE, or "replacement" always yields UTF-8 output because those are their WHATWG-defined output encodings, not the input encoding
- Speed is an explicit non-goal for legacy-encoding encode paths by default; enable `fast-hangul-encode`/`fast-kanji-encode`/etc. (or the `fast-legacy-encode` bundle) if CJK encode throughput matters
- `simd-accel` requires nightly Rust features, so a plain stable build won't get the full multiversioned SIMD dispatch described in the README
- The Cargo license string is a compound `(Apache-2.0 OR MIT) AND BSD-3-Clause`: the BSD-3-Clause part covers WHATWG-derived label/encoding data, not just the code

## Caveats and trade-offs

First-party benchmark (author's own blog, Nov 2016) against ICU 55, a decade-old ICU release built by Ubuntu's toolchain that may not reflect current ICU. The author notes ICU's build flags and compiler may differ from ICU as used in browsers. Only the microarchitecture (Haswell) is given, with no CPU model or rustc version/flags. The benchmark harness is hsivonen/encoding_bench. Some directions (UTF-16LE/BE) are slower than ICU. The Cargo license is '(Apache-2.0 OR MIT) AND BSD-3-Clause'; the BSD-3-Clause part covers WHATWG-derived data.

API differs from ICU (Rust-native, WHATWG Encoding Standard semantics rather than ICU's broader encoding conversion API); no arbitrary encoding support, only WHATWG-listed encodings

## Maintenance

Actively maintained (last commit 2026-09-24, core dependency of Firefox/Gecko and Servo); dual Apache-2.0/MIT plus BSD-3-Clause licensed and small enough to vendor ("copyable"), though the cited benchmark predates two later rewrites of the hot paths.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-25): confirm; tier before verification C, tier now C.
- **Tier reason:** The author's 2016 blog has ratio tables vs ICU 55 (Ubuntu 16.04 build): English UTF-8 decode 7.23 and encode 7.00, other-language UTF-8 decode 1.64-3.92, UTF-16LE/BE 0.30-0.32. The benchmark code is public (hsivonen/encoding_bench), but no CPU model (only 'Haswell') or compiler version/flags are given, so tier C.
- **Verifier notes:** All claimed ratios are on the page (English 7.23/7.00; non-English UTF-8 decode 1.64-3.92; UTF-16 0.30-0.32). The GitHub spdx is NOASSERTION; Cargo.toml plus the LICENSE-APACHE, LICENSE-MIT and LICENSE-WHATWG files give the corrected expression. 467 stars, last commit 2026-09-24, not a fork, not archived.
- **Fields the verifier corrected:** `license`, `caveats`
- **Pages the verifier opened:**
  - <https://hsivonen.fi/encoding-perf-2016-11/>
  - <https://github.com/hsivonen/encoding_rs>
  - <https://github.com/hsivonen/encoding_rs/blob/main/Cargo.toml>
  - <https://github.com/hsivonen/encoding_bench>
- **Sources the enricher read:**
  - <https://github.com/hsivonen/encoding_rs>
  - <https://github.com/hsivonen/encoding_rs/blob/main/Cargo.toml>
  - <https://github.com/hsivonen/encoding_rs/blob/main/src/lib.rs>
  - <https://hsivonen.fi/encoding-perf-2016-11/>
- **Raw records:** [data/wave3/verified.json](../../../data/wave3/verified.json) (id `https://github.com/hsivonen/encoding_rs`) · [data/wave3/enrich/raw/github_com_hsivonen_encoding_rs.json](../../../data/wave3/enrich/raw/github_com_hsivonen_encoding_rs.json) (enrichment confidence 0.7)

</details>
