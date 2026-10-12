# qdgeo

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Numerics and science](../README.md) › [Geometry and spatial](README.md)</sub>

**Tier C** (first-party claim) · Copyable · `Zig` · `MIT` · 🟢 active

> Zig/WASM polygon booleans and rounded buffer for web GIS; 2.7-3.3x faster than native GEOS on a 4,040-parcel union.

| | |
|---|---|
| **Beats** | GEOS 3.13.1 (via Shapely 2.1.2): union, intersection, difference, symmetric difference and buffer |
| **Claimed result** | README Union table (median of three suite runs of 11 repeats): 4,040 parcels qdgeo wasm 160 ms, qdgeo native 130 ms vs GEOS 426 ms; 1,000 parcels 20.3 / 16.8 ms vs 65.7 ms. Derived from page data: 2.7x (wasm) and 3.3x (native) on the full union; the README's Design goals section rounds this to '3.1x native GEOS'. Geometric mean over the 26 workloads: GEOS native 1.5x slower than qdgeo wasm (range across runs 1.36-1.62). Buffer of 100 parcels +2 m: 1.30 ms vs GEOS 4.54 ms. GEOS is faster on the single 19,208-coordinate parcel buffer (+2 m 8.25 ms vs 33.2 ms; -2 m 13.0 ms vs 31.9 ms). |
| **Workload** | 26 boolean/buffer workloads over a 4,040-parcel, 135,080-coordinate public county parcel dataset (GeoMoose demo data); each figure is median of three suite runs of 11 repeats. |
| **Metric** | throughput |
| **Hardware** | One idle machine; CPU model not stated |
| **Compiler and flags** | Zig 0.16.0, zig build native -Doptimize=ReleaseSafe (shipped build keeps safety checks); WASM build run in Node 22+ |
| **Adoption** | 0 stars; very new (first commit 2026-09-14) |
| **Last commit** | 2026-09-23 |
| **Links** | [repository](https://github.com/theduckylittle/qdgeo) · [benchmark](https://github.com/theduckylittle/qdgeo) |

## Verdict

The author's comparison suite (tests/compare, Zig 0.16.0 ReleaseSafe, Node 22+) ran 26 union and buffer workloads on a 4,040-parcel, 135,080-coordinate public GeoMoose dataset. Each figure is the median of three suite runs of 11 repeats, on one unnamed idle machine. Against GEOS 3.13.1 via Shapely 2.1.2, the full union took 160 ms (WASM) and 130 ms (native) vs 426 ms (2.7x and 3.3x, derived from page data; the README rounds this to '3.1x native GEOS'). The geometric mean over all 26 workloads has native GEOS 1.5x slower than qdgeo WASM (1.36-1.62 across runs), and GEOS wins on the 19,208-coordinate single-parcel buffer. Boundaries differ: GEOS times the operation only on prebuilt GEOS objects, while qdgeo native includes a WKB parse and encode round trip. GEOS itself measured 417 ms and 356 ms an hour apart, so gaps under about 20% are unresolved.

## Use it when

- Browser or Node web-GIS apps (OpenLayers, deck.gl, MapLibre, Leaflet) that need union/difference/buffer client-side: GEOS has no supported browser build, and qdgeo was 7-28x faster than JSTS, Turf and polyclip-ts on the author's parcel suite
- Unioning or buffering many adjacent cadastral parcels with hairline gaps and shared boundaries: the full 4,040-parcel union took 160 ms (WASM) or 130 ms (native) vs 426 ms for GEOS 3.13.1, and qdgeo was one of only two engines returning correct geometry there
- Pipelines that would rather get an error than snapped or approximated geometry: qdgeo's disputed vertices matched exact rational reconstruction (0 m error) where GEOS was off by up to 7.2e-5 m
- Small-download constraints: 50.8 KB gzipped vs about 778 KB for geos-wasm (which was not benchmarked)

## Skip it when

- Very large single polygons: on a 19,208-coordinate parcel GEOS buffered +2 m in 8.25 ms vs 33.2 ms (about 4x faster), and 13.0 vs 31.9 ms for -2 m
- Dirty or invalid input you expect the library to fix: qdgeo rejects zero-area or degenerate rings and failed noding instead of repairing them (6 of 161 JTS buffer assertions fail for this reason). Run make_valid/ST_MakeValid or GeoRepair first
- Workloads that need an answer for every valid input: 4 of 3,946 adjacent-parcel cluster unions return an error because f64 cannot hold the crossing. Smaller batches make this more likely (4 failures at 250-parcel batches, 0 at 500-1,000)
- C++ codebases wanting a native library: the core is Zig 0.16, no C header ships, and the native shared library's C ABI (global result block, single-threaded, non-reentrant, errors printed to stderr) is described as built for differential benchmarks
- Anything beyond five areal operations (predicates, line/point outputs, simplification, spatial indexes, CRS handling), or projects that need maturity: first commit 2026-09-14, 0 stars, not published to npm (registry returns 404)

## How it is fast

The overlay is a single Martinez-Rueda sweep line. It uses per-layer winding counts instead of in/out parity (no edge-type classification), orders events lexicographically by (x, y) as a symbolic shear so vertical edges need no special case, and calls exact adaptive orientation predicates at every sign decision. Events are stored structure-of-arrays with order-preserving u128 sort keys, bucketed by x and pdq-sorted within buckets, and the sweep processes all events at one point as a batch. The buffer follows the JTS/GEOS construction: one raw self-intersecting offset curve per ring, line or point, resolved in one overlay pass by keeping regions with winding depth at least 1. The result-vertex hash map is pre-sized to its upper bound with a cheap custom hash. There is no snap-rounding ladder: a failed labelling is retried once with a graph relabelling and once with re-noding, otherwise an error is returned. The WASM build enables simd128.

## Compared with alternatives

Pick qdgeo over clipper2next/Clipper2 or CavalierContours when the target is the browser or you need exact, unsnapped output on GIS parcels rather than integer-lattice C++ clipping. Pair it with GeoRepair, which handles the invalid-geometry repair qdgeo refuses, and use TG for fast point-in-polygon/intersects predicates, which qdgeo does not offer.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | none (pure Zig, no C or C++, WASM declares no imports); the comparison suite needs Python 3.13, Shapely/GEOS, Rust 1.88+ and npm engines |
| **Minimum toolchain** | Zig 0.16.0 (minimum_zig_version); JS consumers need an ESM bundler or Node, and the harness used Node 22+ |
| **Platforms** | wasm32-freestanding with simd128 (browsers, Node, workers; heap capped at 512 MiB), plus any native target Zig builds (static library, or shared libqdgeo_native with a C ABI) |
| **Thread safety** | The flat and WKB host ABI is documented as single-threaded and non-reentrant: one global input block and one global result block, reused across calls. The native Zig API takes an explicit allocator and returns arena-owned Geometry values; its concurrency is not documented |
| **Drop-in for the baseline** | partial: it covers GEOS/Shapely union_all, intersection, difference, symmetric_difference and buffer for polygons (WKB in and out natively), but with a different API, no precision model or repair, and polygon-only results |

## Gotchas

- ABI status 5 means both 'malformed geometry' and 'valid but not representable in f64'. The failure is deterministic, so retrying does nothing, but nudging or rounding the input usually moves past it
- Coordinates are planar in input units and no CRS is read from WKB: reproject lon/lat to a metric CRS before asking for metre buffers
- Buffering several polygons buffers their union, and a zero-distance buffer still runs union and normalisation rather than returning a copy. Output limits are checked after construction, not enforced as an allocation budget
- The shipped WASM is ReleaseSafe (runtime safety checks on). ReleaseFast is 11% faster with bit-identical output if you build it yourself

## Known shortcomings

- No CPU model; the '3.1x' headline vs the table's 2.7x (wasm) / 3.3x (native); the GEOS boundary handling favours GEOS.
- Zig, not C++: no C header; the native C ABI uses global state, is non-reentrant and meant for benchmarks. Not on npm (404); 0 stars, two weeks old. 4/3946 valid cluster unions error by design; GEOS is 4x faster on a 19k-coordinate buffer.

## Caveats and trade-offs

Application-level comparison, and the README admits the boundaries are not equal. GEOS gets shapely.union_all over geometries that are already GEOS objects (no parse or encode), while qdgeo native rows include a WKB parse/encode round trip and the wasm rows a flat-ABI copy. That favors GEOS, though GEOS is native and qdgeo wasm is not. The harness notes GEOS measured 417 ms and 356 ms for the same workload an hour apart, and the README says to treat gaps under 20% as unresolved. GEOS is faster on very large single polygons. The shipped build keeps safety checks (ReleaseSafe; ReleaseFast is 11% faster). qdgeo rejects invalid input instead of repairing it, and it errors on 4 of 3,946 valid cluster unions it cannot node exactly. The project is days old (first commit 2026-09-14), only one dataset (GeoMoose parcels) is tested, and it is not a general GEOS replacement. The CPU model is missing, so tier C.

Only five operations (four booleans and rounded buffer). Rejects invalid geometry instead of repairing it, and valid input can occasionally fail (4 of 3,946 cluster unions) because it declines to snap coordinates. WASM artifact 135 KB raw, 50.8 KB gzipped, no C or C++ dependency; Zig native build has a C-compatible ABI.

## Maintenance

Brand-new (first commit 2026-09-14, last 2026-09-23, 15 commits, 0 stars) and actively developed by one author under MIT, with CI running unit tests, WASM checks and the JTS suite. The 'experimental' label was removed on 2026-09-16, but it has no npm release yet, so install it from git or vendor the WASM artifact.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-09-26): confirm; tier before verification C, tier now C.
- **Tier reason:** First-party README tables against GEOS 3.13.1 (Shapely 2.1.2) over 26 parcel workloads, with a public harness (tests/compare/run.py and probes.py, documented in tests/compare/README.md) and Zig 0.16.0 with -Doptimize=ReleaseSafe stated. The machine is described only as 'one idle machine' with no CPU model, so it is not A.
- **Verifier notes:** Every number in the record matches the README tables. The '3.1x' headline does not exactly match the table, which gives 2.7x for wasm and 3.3x for native, so I spelled out the derived ratios. Metadata from github.com: MIT (LICENSE.txt and package.json), 0 stars, 15 commits, first commit 2026-09-14, last commit 2026-09-23. The JTS test cases bundled under tests/jts are EDL-1.0, test data only.
- **Fields the verifier corrected:** `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** enrichment
- **Pages the verifier opened:**
  - <https://github.com/theduckylittle/qdgeo>
  - <https://github.com/theduckylittle/qdgeo/commits>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/tests/compare/README.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/package.json>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/LICENSE.txt>
- **Sources the enricher read:**
  - <https://github.com/theduckylittle/qdgeo>
  - <https://github.com/theduckylittle/qdgeo/commits>
  - <https://github.com/theduckylittle/qdgeo/issues>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/README.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/tests/compare/README.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/package.json>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/build.zig>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/build.zig.zon>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/LICENSE.txt>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/TODO.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/CLAUDE.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/docs/BUFFER_APPROACH.md>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/src/root.zig>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/src/abi.zig>
  - <https://raw.githubusercontent.com/theduckylittle/qdgeo/HEAD/src/native.zig>
  - <https://registry.npmjs.org/qdgeo>
- **Raw records:** [data/wave8/verified.json](../../../data/wave8/verified.json) (id `https://github.com/theduckylittle/qdgeo`) · [data/wave8/enrich/raw/github_com_theduckylittle_qdgeo.json](../../../data/wave8/enrich/raw/github_com_theduckylittle_qdgeo.json) (enrichment confidence 0.8)

</details>
