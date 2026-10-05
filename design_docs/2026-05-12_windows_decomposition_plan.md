# Windows Producer / Demo Decomposition Plan

**Status (2026-10-05):** decomposition retained; bounded WGC capture-queue
repair implemented and focused tests passing locally, native freshness
acceptance open. The published Turnstone consumer still uses registry 0.7.1.

The Windows browser-parity tranche proved the next WebView2 surface, but it
also made two files violate the repository's 600-LOC module discipline:

- `scrying/src/webview2_composition_producer.rs`: 3666 lines
- `demo-win/src/main.rs`: 2901 lines

The target is the same shape already used by the macOS producer split: small
modules organized by ownership boundary, each kept under roughly 600 lines.
The split should be mechanical first, with behavior-preserving moves and the
existing bounded Windows smokes used after each lane.

## Library Split

Convert `webview2_composition_producer.rs` into a module directory:

- `mod.rs` — public config/types, producer struct, constructor, exports.
- `trait_impl.rs` — `WebSurfaceProducer` implementation.
- `capture.rs` — WGC session setup, frame acquisition, restart, snapshot, and
  resize capture lifecycle.
- `browser.rs` — find-in-page, PDF/print, context-menu events, media-capture
  bridge, and Set-Cookie response observation.
- `cookies.rs` — cookie manager requests, parsing, set/delete, callback API.
- `downloads.rs` — download registry, destination decisions, progress,
  pause/resume/cancel.
- `auth_permissions.rs` — Basic auth and permission request mapping.
- `resources.rs` — virtual-host routing, response construction, stream helpers.
- `input.rs` — mouse, pointer, keyboard, focus, cursor, and OLE drag helpers.
- `helpers.rs` — COM string, message-pump, timeout, and small shared utilities.

The first move should extract `browser.rs` because the newest tranche is a
cohesive unit and has clear demo coverage: `--find-test`, `--pdf-test`,
`--context-test`, `--media-test`, and the Set-Cookie part of `--cookie-test`.

## Demo Split

Convert `demo-win/src/main.rs` into a small app shell plus smoke modules:

- `main.rs` — CLI, `ApplicationHandler`, top-level one-shot dispatch.
- `renderer.rs` — wgpu renderer and imported texture presentation.
- `probe.rs` — startup GraphicsCapture / D3D shared-texture probes.
- `input.rs` — winit input forwarding helpers.
- `smokes/browser.rs` — scripted/browser/visibility/find/PDF/context/media.
- `smokes/network.rs` — virtual host, process recovery, downloads, auth,
  permissions, cookies, and loopback test servers.
- `smokes/profile.rs` — persistent profile, incognito, multi-view.

Start with `smokes/browser.rs` after the library browser split so the newest
runtime lanes stay paired.

## Validation After Each Lane

Use targeted checks, not broad/open-ended GUI runs:

```bash
rustfmt --edition 2024 --check <edited rust files>
cargo check --manifest-path repos/scrying/Cargo.toml -p scrying -p demo-win
```

For GUI/runtime coverage, use the existing bounded PowerShell wrapper with
process-tree cleanup. Do not run raw open-ended `cargo run -p demo-win`.

Minimum smoke set for the first browser split:

```bash
cargo run --manifest-path repos/scrying/Cargo.toml -p demo-win -- --find-test
cargo run --manifest-path repos/scrying/Cargo.toml -p demo-win -- --pdf-test
cargo run --manifest-path repos/scrying/Cargo.toml -p demo-win -- --context-test
cargo run --manifest-path repos/scrying/Cargo.toml -p demo-win -- --media-test
cargo run --manifest-path repos/scrying/Cargo.toml -p demo-win -- --cookie-test
```

All GUI commands above must be wrapped by an external timeout and process-tree
kill during validation.

## Capture queue maintenance (2026-10-05)

### Findings

- `scrying/src/webview2_composition_producer/capture.rs` coalesced all pending
  `FrameArrived` notifications, then dequeued only one sample from a two-slot
  WGC pool. Two paints before a poll followed by an idle page could strand the
  newest queued paint until another arrival. The pinned registry 0.7.1 source
  and the current checkout both contained this mismatch.
- Frozen Turnstone's October 5 consumer receipt reports current DOM titles
  ahead of imported pixels and blank final reconstructed tiles. The queue
  mismatch is an actionable supplier defect and a candidate for the stale
  pixels, not an established explanation for every observed failure. Cookie
  persistence failures remain a separate open diagnostic.

### Phase and done-conditions

The local repair shares the pool capacity with a bounded newest-sample drain
used by both nonblocking and explicit-wait acquisition. Superseded WGC frames
are closed; the selected frame follows the existing size guard, copy, fence,
and custody path. Continuous paint cannot turn acquisition into an unbounded
drain. Arrivals during draining retain their wake notification.

Done requires the two-arrival/no-new-paint regression, its deliberately broken
single-dequeue positive control, empty/single-sample custody, and bounded
continuous-arrival regressions to pass; then a headed Windows receipt must
observe the final static DOM state in imported pixels, including resize and
reconstruction. Counts and DOM/title assertions alone do not close that gate.

### Progress

- **2026-10-05:** `cargo test -p scrying --lib
  webview2_composition_producer::capture::tests --target-dir
  C:/t/cargo-targets/wgpu-scry --locked` compiled the Windows/default wgpu-30
  library and passed all five focused tests (four new, retained reparenting
  test; 22 other tests filtered). `rustfmt --edition 2024 --check
  scrying/src/webview2_composition_producer/capture.rs` and `git diff --check`
  passed. The old-behavior positive control proves that two notifications,
  one dequeue, and no subsequent paint leave frame 2 unread; the repaired
  drain delivers frame 2 and closes frame 1 in that same poll. The stable
  repository target is retained for reuse. No native run, consumer repin,
  package, tag, or publication performed. Existing capture/input and
  platform gates remain qualified in the browser checklist and backlog.
