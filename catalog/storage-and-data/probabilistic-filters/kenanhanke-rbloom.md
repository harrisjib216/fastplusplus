# rbloom

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Storage and data](../README.md) › [Probabilistic filters](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Rust` · `MIT` · 🟢 active

> Rust (PyO3) Bloom filter for Python with a set-like API; beats other PyPI Bloom packages on insert+lookup wall time.

| | |
|---|---|
| **Beats** | Bloom filter |
| **Claimed result** | 2.52s (rbloom) vs 4.78s (pybloomfiltermmap3), 46.76s (pybloom3), 76.94s (Flor), 165.54s (bloom-filter2) -- up to \~65x faster than the slowest compared library (derived from page data) |
| **Workload** | Insert 10,000,000 float keys into a Bloom(10_000_000, 0.01) filter, then look up all 10,000,000 keys, compared against other Python Bloom filter packages (pybloomfiltermmap3, pybloom3, Flor, bloom-filter2). |
| **Metric** | throughput |
| **Hardware** | Apple M1 Pro ("confirmed to be proportional to runtimes on an Intel machine") |
| **Adoption** | 318 stars; archived on Zenodo (DOI 10.5281/zenodo.17084925) |
| **Last commit** | 2025-11-23 |
| **Links** | [repository](https://github.com/KenanHanke/rbloom) · [benchmark](https://github.com/KenanHanke/rbloom#benchmarks) |

## Verdict

The README table comes from the in-repo benchmarks/compare.py: insert 10M float keys into Bloom(10_000_000, 0.01), then look all of them up, averaged over 5 timeit runs on an Apple M1 Pro. rbloom took 2.52 s, versus pybloomfiltermmap3 4.78 s (\~1.9x), pybloom3 46.76 s (\~18.6x), Flor 76.94 s (\~30.5x) and bloom-filter2 165.54 s (\~65.7x); ratios are derived from page data. The timings are whole-loop wall time including the Python interpreter loop. Flor and bloom-filter2 ran through a struct.pack-to-bytes fallback that adds per-key packing cost. Competitor versions are pinned in requirements.txt (pybloomfiltermmap3 0.6.0, pybloom3 0.0.3, flor 1.1.3, bloom-filter2 2.0.0), but the Python version, rustc version and wheel build flags are not stated. The table was last updated in the 2024-10-01 'Reflect benchmark changes' commit, and nothing was compared against a native C/C++ Bloom filter.

## Use it when

- Python code that needs a probabilistic 'seen before?' set over arbitrary hashable objects (str, tuples, floats, frozen dataclasses), such as URL or record dedup when a real `set` would not fit in RAM (about 9.6 bits per key at 1% FPR, derived from the sizing formula).
- Replacing pybloom3, Flor or bloom-filter2 in a loop-heavy Python pipeline: the README table shows 18-66x lower wall time than those three (derived from page data).
- Replacing pybloomfiltermmap3 when you don't need its mmap file backing: about 1.9x faster in the same table, and it installs from prebuilt abi3 wheels (the README reports pybloomfiltermmap3 failing to install on 3.11 and segfaulting on 3.10 in January 2023, but fine by October 2024).
- Building filters in several processes or shards and merging them with `|` / `update` or comparing them with `issubset`, as long as every filter uses the same deterministic custom `hash_func` object and the same (n, p) parameters.
- Deployments without a Rust toolchain on mainstream platforms: PyPI ships cp37-abi3 wheels for manylinux x86_64/i686/aarch64/armv7l/ppc64le/s390x, macOS x86_64/arm64 and Windows win32/amd64.

## Skip it when

- Throughput-critical bulk work: every operation pays Python call and interpreter-loop overhead. The README run works out to about 126 ns per operation (2.52 s / 20M ops, derived). A user in issue #23 measured 8.89M queries/s on an M4 Pro. There is no vectorized NumPy/Arrow insert or query API (issue #23 is open). From Rust, C or C++, use a native filter instead.
- You need deletion, counting, a real length, or auto-growth. It is a plain fixed-size Bloom filter: going past `expected_items` silently raises the FPR, and `approx_items` is an O(m) popcount over the whole bit array (issue #25 asks for O(1)).
- Large, memory-bound filters where cache misses dominate. The layout is unblocked, so each operation makes k independent random bit probes over the whole array. There is no blocked, SIMD, xor, or ribbon variant, so both space and probes per operation are worse than those designs.
- You need a file-backed, mmap-ed or zero-copy shared filter (pybloomfiltermmap3 does this), or you want to pickle it. Pickle is refused by design (issue #16). `save`/`load` work only with a user-supplied deterministic `hash_func`, because the built-in `hash()` is salted per process.
- Free-threaded CPython (3.13t+), multi-core parallel queries, PyPy, or musl/Alpine. The module does not declare `gil_used = false`, so per PyO3 docs a free-threaded interpreter turns the GIL back on at import. No 3.13t, PyPy or musllinux wheels are published, so those builds compile from source with Rust and maturin.

## How it is fast

Each `add` or `in` makes one call into compiled Rust. The object is hashed once, with Python's `hash()` (an isize) or the user's `hash_func` (up to i128). That single hash seeds a 128-bit linear congruential generator (multiplier from L'Ecuyer 1999), which produces all k bit indices. This is the one-hash-many-indices trick, similar in spirit to Kirsch-Mitzenmacher double hashing. Bits live in a plain `Box<[u8]>`, each index is `x % m`, and lookups stop at the first zero bit. Sizing is textbook: m = -n ln p / ln^2 2 and k = floor(log2(1/p)). There is no blocking, SIMD, or GIL release, so the speedup comes from moving hashing and bit work out of interpreted Python, not from a better filter layout.

## Compared with alternatives

Pick rbloom when your code is Python and you want a mutable, set-like filter over arbitrary Python objects from a pip-installable wheel. Every catalogued sibling is a C/C++/Rust/Go/GPU library with no Python API here. If you are writing Rust, fastbloom (one-hash-derived indices plus a lock-free AtomicBloomFilter) or xorf (static xor/binary-fuse filters, smaller and faster to query but built once) are better. efficient/cuckoofilter is the choice when you need deletions.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none at runtime; build from source needs PyO3 0.27 (main; the 1.5.4 release used 0.26) and maturin &gt;=1.0,&lt;2.0 |
| **Minimum toolchain** | CPython 3.7+ (abi3-py37 wheels); source builds need Rust 1.74+ (PyO3 0.26/0.27 MSRV) and maturin 1.x |
| **Platforms** | Prebuilt wheels: Linux (manylinux) x86_64, i686, aarch64, armv7l, ppc64le, s390x; macOS x86_64 and arm64; Windows x86 and x64. Other platforms, including PyPy, musl and free-threaded CPython, build from the sdist. |
| **Thread safety** | Not documented by the project. The code relies on PyO3's default runtime borrow checking and never releases the GIL, so calls are serialized and give no multi-core speedup. `add`/`update` hold a mutable borrow while calling the Python-level hash, so another thread touching the same filter at that moment can get a RuntimeError ('already borrowed'), as the PyO3 thread-safety guide describes. On free-threaded builds, importing the module turns the GIL back on. |
| **Drop-in for the baseline** | partial — the core `Bloom(n, p)`, `.add(x)`, `x in bf` shape matches the other Python Bloom packages in compare.py, and the rest copies `set`. But there is no mmap/file-backed mode, persistence requires a custom `hash_func`, pickle is unsupported, and filters can be combined only if (n, p) and the hash-function object are identical. |

## Gotchas

- `false_positive_rate` above 0.5 gives k = floor(log2(1/p)) = 0 hash probes. Such a filter never sets a bit, so every `x in bf` is True and `bool(bf)` is always False. The tests construct Bloom(1140, 0.999) but never exercise membership on it. Because k is floored rather than rounded, p=0.01 uses 6 probes and p=0.001 uses 9, so the real FPR lands slightly above target (derived from the constructor arithmetic).
- The default `hash()` is salted per process and follows Python equality (1, 1.0 and True collide on purpose), so a default-hash filter can't be saved or shared across processes. A custom `hash_func` must return an int in [-2^127, 2^127-1]: unsigned 128-bit digests such as xxh3_128_intdigest raise OverflowError (issue #22). Each call to it costs a Python function call.
- The persistence format is 8 bytes of little-endian k followed by raw bits, with no magic number, stored length, n/p or checksum. A truncated or corrupted file loads silently with a different bit length. Every index is `% len`, so that shows up as false negatives rather than an error. `load_bytes` on fewer than 8 bytes hits a Rust slice panic, surfaced as PanicException. The hash function passed to `load` must match the one used to build the filter, and nothing checks this.
- Set operations and comparisons require the exact same hash-function object (identity, not equality) and identical (n, p). Otherwise they raise ValueError. The `rbloom.pyi` stub also declares `load_bytes` without `@classmethod`, which can confuse type checkers.

## Known shortcomings

- The large multiples are vs pure-Python Bloom libraries; vs the C-extension pybloomfiltermmap3 it is only \~1.9x (derived).
- Python call overhead dominates (\~126 ns/op derived) and there is no vectorized API (#23); a plain unblocked Bloom filter with no SIMD. p&gt;0.5 gives k=0 so every membership test returns True (silently useless, untested); k is floored so FPR slightly exceeds the target.
- Persistence is raw k+bits with no header/checksum, so a truncated file gives silent false negatives; the default hash cannot be saved/pickled; custom hashes are capped to signed i128 (#22). The GIL is never released; custom Python hashes can raise 'already borrowed' across threads; importing re-enables the GIL on free-threaded builds; no 3.13t/PyPy/musl wheels. CI runs no tests.

## Caveats and trade-offs

Benchmark script (benchmarks/compare.py) is in-repo but rustc/maturin flags used to build the wheel for the timing run are not stated on the page; comparison is against other Python bindings, not a bare-metal C/C++ Bloom filter.

Implemented in Rust with a Python API (PyO3), compiled against a stable ABI (abi3) for portability at a small perf cost vs building from source; does not use mmap so no zero-copy persistence like pybloomfiltermmap3.

## Maintenance

MIT-licensed, a single 682-line lib.rs with 318 stars and a Zenodo DOI. Maintenance is low-cadence and bursty: the last PyPI release is 1.5.4 (2025-09-09, PyO3 0.26), the last commit (2025-11-23) only bumped PyO3 to 0.27 and is unreleased, and three feature requests (#22, #23, #25) are open. CI builds wheels but does not run tests/api_test.py.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party timing table from the in-repo script benchmarks/compare.py on an M1 Pro. Python, rustc and build flags are not stated, so this is partial methodology and stays C.
- **Verifier notes:** All five timings (2.52/4.78/46.76/76.94/165.54 s) match the README table exactly, and the \~65x is correctly marked as derived. Against the nearest competitor, pybloomfiltermmap3 (a C/Cython extension), the gain is only \~1.9x (derived from page data). Metadata checks out: MIT, 318 stars, last commit 2025-11-23, not archived, not a fork, Zenodo DOI badge present.
- **Pages the verifier opened:**
  - <https://github.com/KenanHanke/rbloom>
  - <https://github.com/KenanHanke/rbloom#benchmarks>
  - <https://github.com/KenanHanke/rbloom/blob/main/benchmarks/compare.py>
  - <https://github.com/KenanHanke/rbloom/blob/main/Cargo.toml>
- **Sources the enricher read:**
  - <https://github.com/KenanHanke/rbloom>
  - <https://github.com/KenanHanke/rbloom#benchmarks>
  - <https://github.com/KenanHanke/rbloom/blob/main/src/lib.rs>
  - <https://github.com/KenanHanke/rbloom/blob/main/Cargo.toml>
  - <https://github.com/KenanHanke/rbloom/blob/main/pyproject.toml>
  - <https://github.com/KenanHanke/rbloom/blob/main/rbloom.pyi>
  - <https://github.com/KenanHanke/rbloom/blob/main/benchmarks/compare.py>
  - <https://github.com/KenanHanke/rbloom/blob/main/benchmarks/per_operation.py>
  - <https://github.com/KenanHanke/rbloom/blob/main/benchmarks/requirements.in>
  - <https://github.com/KenanHanke/rbloom/blob/main/benchmarks/requirements.txt>
  - <https://github.com/KenanHanke/rbloom/blob/main/tests/api_test.py>
  - <https://github.com/KenanHanke/rbloom/blob/main/.github/workflows/CI.yml>
  - <https://github.com/KenanHanke/rbloom/commits/main>
  - <https://github.com/KenanHanke/rbloom/issues>
  - <https://github.com/KenanHanke/rbloom/issues/13>
  - <https://github.com/KenanHanke/rbloom/issues/14>
  - <https://github.com/KenanHanke/rbloom/issues/16>
  - <https://github.com/KenanHanke/rbloom/issues/17>
  - <https://github.com/KenanHanke/rbloom/issues/19>
  - <https://github.com/KenanHanke/rbloom/issues/22>
  - <https://github.com/KenanHanke/rbloom/issues/23>
  - <https://github.com/KenanHanke/rbloom/issues/25>
  - <https://pypi.org/pypi/rbloom/json>
  - <https://github.com/PyO3/pyo3/blob/v0.27.0/README.md>
  - <https://github.com/PyO3/pyo3/blob/v0.26.0/README.md>
  - <https://github.com/PyO3/pyo3/blob/v0.27.0/guide/src/free-threading.md>
  - <https://github.com/PyO3/pyo3/blob/v0.27.0/guide/src/class/thread-safety.md>
  - <https://github.com/tomtomwombat/fastbloom>
  - <https://github.com/ayazhafiz/xorf>
  - <https://hn.algolia.com/api/v1/search?query=rbloom&tags=story>
- **Raw records:** [data/wave6/verified.json](../../../data/wave6/verified.json) (id `https://github.com/kenanhanke/rbloom`) · [data/wave6/enrich/raw/github_com_kenanhanke_rbloom.json](../../../data/wave6/enrich/raw/github_com_kenanhanke_rbloom.json) (enrichment confidence 0.85)

</details>
