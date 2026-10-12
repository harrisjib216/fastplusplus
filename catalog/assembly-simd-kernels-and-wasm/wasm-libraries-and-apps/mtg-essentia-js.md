# Essentia.js

<sub>[fastpp](../../../README.md) › [Catalog](../../README.md) › [Assembly, SIMD and WebAssembly](../README.md) › [WebAssembly libraries and apps](README.md)</sub>

**Tier D** (directional, no numbers) · Copyable · `C++ (Essentia) compiled to WebAssembly with a JavaScript API` · `AGPL-3.0` · 🔴 abandoned

> Essentia's C++ audio-analysis library compiled to WebAssembly with a JS/TypeScript API; papers benchmark it against Meyda, results unread.

| | |
|---|---|
| **Beats** | Meyda (pure-JS audio feature extraction) and native Essentia; the paper benchmarks against both |
| **Claimed result** | No numbers seen. The TISMIR 2021 paper (Correya et al., doi 10.5334/tismir.111) and the ISMIR 2020 paper benchmark Essentia.js against native Essentia and the Meyda JS library (two browsers, Node.js, four devices including Android and iOS, per search snippets), but the results, and whether Essentia.js was faster than Meyda, could not be read. |
| **Workload** | Audio feature extraction benchmarks in two browsers, Node.js and four devices including Android and iOS (per paper abstracts seen in search snippets). |
| **Metric** | latency |
| **Adoption** | 870 stars |
| **Last commit** | 2022-07-19 |
| **Links** | [repository](https://github.com/MTG/essentia.js) · [benchmark](https://github.com/MTG/essentia.js-benchmarks) |

## Verdict

No measured result could be read: the ISMIR 2020 and TISMIR 2021 papers time Essentia.js against Meyda and native Essentia on two browsers, Node.js and four devices (Android, iOS), but every copy was blocked here, and the benchmark repo commits no results. Whether Essentia.js beats Meyda, and by how much, is unverified; the browser harness behind the papers has a frame-count asymmetry and mismatched algorithm parameters.

## Use it when

- You need MIR algorithms that pure-JS libraries lack (key and chord detection, Melodia/PYIN pitch, beat trackers, EBU R128, NNLS chroma) in a browser, Web Worker, AudioWorklet or Node.js.
- You want the same algorithms and defaults as a native or Python Essentia pipeline, so web results match server-side features.
- Offline whole-file analysis where a few heavy calls (RhythmExtractor2013, KeyExtractor, TensorflowInputMusiCNN) dominate and the per-call setup cost is amortised.
- Feeding the bundled Essentia TensorFlow.js models (MusiCNN, VGGish auto-tagging, mood, genre) from the same feature code used to train them.
- AGPL-3.0 is acceptable for your web app, or you can buy a commercial Essentia licence from UPF.

## Skip it when

- Closed-source or SaaS products that cannot meet AGPL-3.0 (network use counts as distribution).
- Per-frame calls of cheap features (energy, RMS, ZCR, centroid) in a tight loop: every call re-creates the C++ algorithm and copies data across the JS/wasm boundary, while Meyda caches its mel filterbank between calls; a pure-JS library may be competitive there, and no published number settles it.
- Code that cannot manage memory by hand: every VectorFloat returned must be `.delete()`d or the wasm heap grows.
- Projects needing a maintained npm package: the last npm release is 0.1.3 (2021-06-24), master's last commit is 2022-07-19 and only a dev branch moved (2024-06-12); the README still says APIs are unstable.
- Bundle-size-sensitive pages: the sync UMD/ES builds embed the whole wasm binary as base64 (SINGLE_FILE=1).

## How it is fast

Speed comes only from running Essentia's C++ (Emscripten 1.39.19, KISS FFT backend, Eigen) as WebAssembly instead of interpreting pure-JS DSP. The build is not tuned for speed: Makefile.essentiajs compiles with -Oz (size), keeps ASSERTIONS=2 and EXCEPTION_DEBUG in the web build, and uses no wasm SIMD or threads. The generated wrapper (src/cpp/includes/essentiajs.cpp) creates, configures and deletes a new algorithm instance through AlgorithmFactory on every call, so per-frame use pays for filterbank, window and FFT setup each frame; issue #65 reports the unmerged class-based (configure-once) interface gave a 'significant' MFCC speedup, without numbers.

## Compared with alternatives

Pick it over tinyfft when you need complete MIR features (MFCC, key, beats, pitch) rather than a raw FFT. Pick it over the TensorFlow.js WASM backend when you need Essentia's audio preprocessing to feed models trained on Essentia features; it uses tfjs for the models themselves.

## Integration

| | |
|---|---|
| **Form** | module |
| **Dependencies** | npm essentia.js (wasm backend plus JS/TS API; node-wav for Node file loading); optional @tensorflow/tfjs for the model add-on and Plotly for plots. Rebuilding needs the Dockerfile's Emscripten 1.39.19 image with Essentia built statically (--fft=KISS) and Eigen 3.3.7. |
| **Minimum toolchain** | Any browser with WebAssembly (Web Audio API for decoding); Node.js (build scripts use Node 12.18.1); TypeScript 3.9 for the typings. |
| **Platforms** | Browsers (the papers test two desktop browsers plus Android and iOS devices; the benchmark page names Chrome and Firefox), Node.js, Web Workers and AudioWorklet; wasm32 only, no SIMD or threaded build. |
| **Thread safety** | not documented; single-threaded wasm module, one instance per worker |
| **Drop-in for the baseline** | no |

## Gotchas

- Benchmark harness flaw (MTG/essentia.js-benchmarks, browser suite src/js/Benchmarks/offline/\*.js): the default 'essentia' frame mode calls FrameGenerator, which drops frames that isSilent() flags (essentiajs.cpp line 91) and uses FrameCutter's own framing, while the Meyda side processes every hop of audioBuffer.length/HOP_SIZE frames, so the two sides do not process the same frames; per-algorithm defaults also differ (Essentia MFCC 40 mel bands vs Meyda 26), so timings are not like for like.
- The Node runner (node/benchmark/\*.js) feeds both libraries the raw WAV file bytes from fs.readFile (header included, never decoded), and index.js forks all suites at once so they contend for CPU. The repo commits no results and pins essentia.js 0.0.9, so it cannot reproduce the papers' figures.
- The native-Essentia baseline (python/essentia_algorithms.py) configures each algorithm once outside the frame loop, while Essentia.js re-creates it per frame. Any wasm-vs-native gap reported from this harness therefore mixes wasm overhead with per-call setup cost.
- Open correctness bugs: VectorFloat params mis-converted from TypeScript (#136), float params accept numeric strings (#137), FrequencyBands throws uncaught (#108), PitchMelodia returns zeros on microphone input (#149), wrong key output reported (#143).

## Known shortcomings

- Downgraded C to D: the TISMIR paper, UPF repo and publisher hosts are blocked, so there are no numbers and no result direction; MTG/essentia.js-benchmarks has no committed results and its node runner feeds raw undecoded WAV bytes and forks all 24 suites at once. Retier candidate if the paper becomes reachable.
- Papers still unreachable (transactions.ismir.net, archives.ismir.net, dokk.org blocked), so no numbers. Browser-suite harness flaws: FrameGenerator drops silent frames while the Meyda side processes every hop, so the frame sets differ; MFCC uses 40 vs 26 mel bands. The generated C++ wrapper re-creates and configures the algorithm on every call while the native Python baseline configures once, so the wasm-vs-native gap mixes in setup cost. Build is -Oz with ASSERTIONS=2, KISS FFT, no SIMD. Dev branch active until 2024-06-12, npm 0.1.3 (2021).

## Caveats and trade-offs

Lead only: no speedup figure or direction of result was verified; a verifier with paper access should read the TISMIR results section. Benchmark harness lives in MTG/essentia.js-benchmarks (AGPL-3.0, 7 stars, last commit 2021-09-02): node/benchmark/\*.js run benchmark.js suites 'Meyda#X' vs 'Essentia#X' over 24 algorithms, python/ runs pytest-benchmark on native Essentia; no results files are committed. Harness flaws seen in node/benchmark/MFCC.js and index.js: both paths are fed the raw WAV file bytes from fs.readFile (header included, never decoded to float samples), the two paths do different per-frame work (Meyda slices and re-sets bufferSize per frame, Essentia adds explicit Windowing), and index.js forks all 24 benchmark scripts at once so they contend for CPU; whether the paper used this runner is unknown. Main repo has no benchmark directory; last commit 2022-07-19, abandoned.

AGPL-3.0 licence; the underlying Essentia C++ library has its own licensing terms (README points to essentia.upf.edu).

## Maintenance

Stale rather than dead: npm 0.1.3 (2021-06), master last commit 2022-07-19, a dev branch active until 2024-06-12 toward a 1.0 roadmap and new issues still filed in 2026; AGPL-3.0, usable from npm without building, but an evidence tier of D: the catalogue entry rests on unread papers and a flawed harness.

<details>
<summary><b>Audit trail</b></summary>

- **Verification** (2026-10-11): downgrade; tier before verification C, tier now D.
- **Tier reason:** No numbers were found anywhere reachable: the TISMIR 2021 paper (doi 10.5334/tismir.111), the UPF repository copy and the publisher mirror were all DNS-blocked here, search snippets give only the benchmark setup (two browsers, Node.js, four devices, vs native Essentia and Meyda) and not the results or their direction, and the MTG/essentia.js-benchmarks harness repo publishes no results. With benchmark_url null and no numbers page found, the record cannot stay above D.
- **Verifier notes:** Downgrade C to D: paper and publisher pages blocked, no numbers or direction of the Meyda comparison found; benchmark harness repo found (MTG/essentia.js-benchmarks) but it publishes no results and its node runner feeds undecoded WAV bytes and runs all suites concurrently. Notable as a peer-reviewed, widely used library (870 stars), so kept rather than rejected; retier candidate if the TISMIR PDF becomes reachable.
- **Fields the verifier corrected:** `benchmark_url`, `claimed_speedup`, `caveats`
- **Shortcomings recorded by:** verifier batch-14 (wave 13); enricher (wave 13 pass, 2026-10-12)
- **Pages the verifier opened:**
  - <https://github.com/MTG/essentia.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/README.md>
  - <https://github.com/MTG/essentia.js/commits/master>
  - <https://github.com/MTG/essentia.js/tree/master/docs>
  - <https://github.com/MTG/essentia.js-benchmarks>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/README.md>
  - <https://github.com/MTG/essentia.js-benchmarks/commits/master>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/src>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/node>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/node/benchmark>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/python>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/dist>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/node/benchmark/MFCC.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/node/benchmark/index.js>
- **Sources the enricher read:**
  - <https://github.com/MTG/essentia.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/README.md>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/package.json>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/CHANGELOG.md>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/Makefile.essentiajs>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/build-libs.sh>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/index.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/Dockerfile>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/src/typescript/core_api.ts>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/src/cpp/includes/essentiajs.h>
  - <https://raw.githubusercontent.com/MTG/essentia.js/HEAD/src/cpp/includes/essentiajs.cpp>
  - <https://github.com/MTG/essentia.js/tree/master/src>
  - <https://github.com/MTG/essentia.js/commits/dev>
  - <https://github.com/MTG/essentia.js/issues>
  - <https://github.com/MTG/essentia.js/issues?q=is%3Aissue+performance+OR+slow+OR+memory+OR+leak>
  - <https://github.com/MTG/essentia.js/issues/65>
  - <https://registry.npmjs.org/essentia.js>
  - <https://registry.npmjs.org/meyda>
  - <https://raw.githubusercontent.com/meyda/meyda/HEAD/src/main.ts>
  - <https://github.com/MTG/essentia.js-benchmarks>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/README.md>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/package.json>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/index.html>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/webpack.config.js>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/src/js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/index.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/test.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/utils/getFile.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/Benchmarks/offline/suite_mfcc.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/Benchmarks/offline/suite_energy.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/src/js/Benchmarks/offline/suite_spectral_centroid.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/node/benchmark/MFCC.js>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/node/benchmark/index.js>
  - <https://github.com/MTG/essentia.js-benchmarks/tree/master/python>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/python/test_essentia.py>
  - <https://raw.githubusercontent.com/MTG/essentia.js-benchmarks/HEAD/python/essentia_algorithms.py>
  - https://transactions.ismir.net/articles/111/files/submission/proof/111-1-2905-1-10-20211122.xml (blocked, ENOTFOUND)
  - https://dokk.org/library/essential.js_javascript_library_for_music_and_audio_analysis_on_the_web_2020 (blocked, ENOTFOUND)
  - https://archives.ismir.net/ismir2020/paper/000260.pdf (blocked, proxy 403 and ENOTFOUND)
- **Raw records:** [data/wave13/verified.json](../../../data/wave13/verified.json) (id `https://github.com/mtg/essentia.js`) · [data/wave13/enrich/raw/github_com_mtg_essentia_js.json](../../../data/wave13/enrich/raw/github_com_mtg_essentia_js.json) (enrichment confidence 0.5)

</details>
