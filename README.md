# wgpu-scry

System-webview frame adapter for wgpu hosts. The [`scrying`](scrying/)
library embeds the platform webview (WebView2, WKWebView, WebKitGTK, WPE),
produces frames the host renderer can consume as GPU textures or CPU
snapshots, and forwards navigation, input, and browser-surface APIs back to
the page.

Extracted from
[`wgpu-graft`](https://github.com/merely-made/wgpu-graft) on 2026-05-05.

## Status (2026-10-05 source audit)

`scrying` 0.7.1 is the published callback-order release. The retained registry-only
triplet receipt covers WebView2/DX12, WKWebView/Metal on M4 and Intel, and
WPE/Vulkan on RADV; it does not establish identical browser capabilities across
all five backends. See `wgpu-graft/design_docs/2026-09-03_wgpu_triplet_release_plan.md`.
Native frame resources have move-only, RAII custody, and the primary WebView2, WKWebView,
and WPE producers expose correlated asynchronous script results through one
ordered event queue. It carries feature-selected wgpu 28/29/30, defaults to
wgpu 30, and requires at least wgpu 30.0.1 on that row.

- Frame transports are proven per platform: Windows WebView2 capture into a
  shared D3D11 texture imported by wgpu D3D12 (the reference
  implementation); macOS WKWebView via ScreenCaptureKit and IOSurface into
  Metal (macOS 14+); Linux WebKitGTK 4.1 and 6.0 via CPU snapshot; Linux WPE
  via DMABUF into Vulkan.
- Beyond frames, the `WebSurfaceProducer` trait covers navigation, history,
  input, ordered events, correlated script results, and cookies. Concrete
  producers additionally expose backend-specific custom schemes, downloads,
  profiles, popups, find, and PDF APIs. These are not all methods on the portable
  trait or reachable through downstream adapters. Per-backend caveats live in
  [`docs/parity-matrix.md`](docs/parity-matrix.md).
- DX12, Metal, and Vulkan/DMABUF imports delegate to published `grafting`
  0.6.0; Scry keeps webview and sync policy.
- CI runs the macOS suite, the WebKitGTK 4.1 Linux suite, and a required Fedora
  44 WPE producer/demo build on every push.

`main` includes September 11 macOS capture-status diagnostics beyond the
published September 4 receipt. Its manifest still reads 0.7.1; that source
reconciliation was not published. The October 4 headed run on that exact source
passed M4 and Windows; Intel failed the base capture cadence assertion, and
RADV failed its session preflight before WPE tests ran. Native diagnostic output
now exists, but the counter unit test and complete affected-platform acceptance
remain open. See the
[diagnostics record](design_docs/2026-05-07_platform_ceilings.md#macos-capture-status-diagnostics-2026-09-11)
and [next-release gates](design_docs/2026-06-28_improvement_backlog.md#next-release-and-consumer-gates).

Open items are a native GTK4 input path for webkit6 (current input is
JS-synthesized), crash recovery for webkit6/WPE, broader IME parity, and
webkit6 zero-copy import. WPE Vulkan DCC sampling is now a hard green gate on
AMD Renoir/RADV; the headed hardware command and receipt are documented in
[`docs/wpe-deployment.md`](docs/wpe-deployment.md#wgpu-vulkan-pixel-correctness-receipt).

## Use

For wgpu hosts that want a system webview rendered inside their own pipeline:

```toml
[dependencies]
scrying = "0.7"

# Hosts on an adjacent wgpu major select it explicitly.
scrying = { version = "0.7", default-features = false, features = ["wgpu-29"] }
```

The default wgpu row is 30. `wgpu-28`, `wgpu-29`, and `wgpu-30` are carried;
disable default features when selecting 28 or 29. On Linux, combine that row
with one of `webkitgtk-fallback`, `webkit6`, or `wpe`. Omitting all three keeps
the WPE producer type available as a compile-only shell; `wpe` enables its
WPEPlatform FFI and live DMABUF production.

Each backend has a runnable demo probe with flagged assertion modes. The
cross-platform probe intentionally pins wgpu 30 and selects scrying's
`wgpu-30` feature, so it is a compiled host-side type-identity receipt rather
than merely another library check:

```sh
cargo run -p demo-scrying-winit   # cross-platform backend-selection smoke
cargo run -p demo-win             # Windows; ~18 --*-test assertion flags
cargo run -p demo-mac             # macOS; bash scripts/test-mac.sh runs the suite
cargo run -p demo-linux           # WebKitGTK 4.1; bash scripts/test-linux.sh
cargo run -p demo-linux6          # WebKitGTK 6.0
cargo run -p demo-wpe             # WPE (see docs/wpe-deployment.md)
```

Deeper documentation: [`scrying/README.md`](scrying/README.md) (producer
contract and GPU sync), [`docs/parity-matrix.md`](docs/parity-matrix.md),
and [`docs/wpe-deployment.md`](docs/wpe-deployment.md).

## Siblings

The family splits engine embedding by target:
[`wgpu-graft`](https://github.com/merely-made/wgpu-graft) (Servo, plus the
shared `grafting` interop core), `wgpu-scry` (system webviews), and
[`wgpu-weld`](https://github.com/merely-made/wgpu-weld) (CEF/Chromium).

## License

[MPL-2.0](LICENSE). The `scrying::native_frame` module is structurally
derived from Slint's MIT-licensed Servo embedding example; see
[NOTICE](NOTICE).
