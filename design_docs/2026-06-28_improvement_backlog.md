# Improvement backlog

Prioritized, actionable follow-ups for `scrying`, distinct from the descriptive
[capability parity matrix](../docs/parity-matrix.md) (which documents *what works
where*). This lists *what to do next* and why. Library work belongs here;
host and adapter work remains with its owning repository.

**Status (2026-11-01):** reconciled against git and the retained release
receipts. Scry 0.7.1 (2026-09-04) closed ownership/import and ordered-completion
work. Scry 0.7.2 (published 2026-10-07, tag `scrying-v0.7.2`) shipped the
macOS capture-status diagnostics, the bounded WGC queue repair, the WPE
main-thread guard and the explicit WebView2 render-tick wait; the repaired RADV
session preflight passed natively. Open: the Intel capture gate (fresh
published-package battery 9/10, activity probe 1/2), the capture-status counter
test, and native Windows final-static-pixel acceptance. No build, native test,
hardware dispatch, or publication was performed by this audit.

## Release mechanical closure (2026-09-03)

This historical slice closed Scry-owned release defects while Graft ownership
was a separate dependency. The WPE capability report claims
DMABUF import only when the `wpe` feature is present, and the combined host
probe downgrades to `HostBackendUnavailable` without a host or to an explained
unsupported mode when the Vulkan extensions are absent. WebKitGTK 4.1 and 6.0
retain each configuration's `frame_timeout`, and their ordinary frame path
overrides the trait default so it never invokes a blocking snapshot from the
render-loop poll. The package README disclaimer was removed. Exact checks and
the subsequent ownership closure are recorded in the progress log below.

### Progress

- **2026-09-03 — landed in this slice:** WPE capability honesty, host-probe
  downgrade behavior, GTK 4.1/6.0 configured snapshot timeout, genuinely
  non-blocking GTK polling, compile-only WPE regression tests, and public
  README cleanup.
- **2026-09-03 — initially deferred to Graft Phase 1:** move-only `NativeFrame`
  ownership and by-value import. This dependency closed in the September 4
  release train; the former borrowed-frame migration is not an open item.
- **2026-09-03 — capability matrix landed:** `WebSurfaceCapabilities::features`
  now reports those domains explicitly, with structured cookie-attribute
  statuses and `Partial` caveats for pointer metadata, drag payloads, IME
  preedit, and Safari inspector attachment. The neutral shared-contract
  extraction remains a separate assessment; this matrix does not adapt Graft
  or change Inker's dependency.

- **2026-09-04 — release closure:** published Scry 0.7.1 consumes Graft 0.6.0
  one-way from the registry. Native descriptors retain move-only custody until
  import, and DX12/Metal/Vulkan import delegates to Graft while Scry keeps its
  producer and synchronization policy. Registry-only four-host run `33916390001`
  covers exact Graft 0.6.0, Scry 0.7.1, and Weld 0.14.1. Detailed evidence and
  limitations live in `wgpu-graft/design_docs/archive_docs/2026-11-01/2026-09-03_wgpu_triplet_release_plan.md` (open work continues in `wgpu-graft/design_docs/2026-11-01_triplet_release_plan.md`).
- **2026-09-04 — WPE DCC closure:** the wgpu-30 DMABUF path is pixel-verified
  on AMD Renoir/RADV. Foreign-queue acquire and the HAL resource-state boundary
  are handled by Graft; this is not waiting on a new wgpu initial-state API.
  Keep the exact [pixel receipt](../docs/wpe-deployment.md#wgpu-vulkan-pixel-correctness-receipt)
  separate from browser-host or other-adapter acceptance.

## Fedora / macOS work

- **WebKitGTK 6.0 input fidelity.** webkit6 input is JS-event-synthesis only, so
  events arrive `isTrusted === false`; pages that gate on it (autoplay,
  `requestFullscreen`, some click-fraud defenses) reject them. GTK 4 removed
  `gtk_main_do_event`, so the GTK 3 native-dispatch primary has no analog. Fix:
  a `gtk4::GestureClick` / `GdkSurface` event-queue path. See parity-matrix
  `[^wk6-input-js-only]`. Highest real-site-compat leverage.
- **Process-crash recovery.** Neither webkit6 nor WPE wires a
  `web-process-terminated` recovery handler, and WPE couples one `WebKitWebView`
  to one process-global headless display (a second producer SIGABRTs/hangs). Add a
  recovery handler and document/enforce the one-producer-per-process (or
  subprocess-per-producer) model. See `[^wpe-process]`, `[^wk6-process]`.
- **IME completion and host integration.** WebView2 already reports editable
  focus/change/blur and caret state, and its host-owned winit/CDP IME bridge has
  a retained smoke receipt. Full Windows TSF parity and multi-pane IME remain
  open. WKWebView native input forwarding and portable editable-state
  observability are distinct claims; the latter remains unverified in the
  parity matrix. Downstream Mere currently reduces WebView2 editable-state
  payloads to diagnostics rather than retaining the host bridge data.
- **Close the test-coverage `?` rows.** Touch (every backend), macOS IME observability, and
  find/pdf/profile (webkit6) are all "no test flag exercises it." Build out the
  cross-backend trait-test infra so guesses become verified ✔/✘ rows.

## Upstream-blocked (track, not actionable here)

- **WebKitGTK 6.0 zero-copy import.** Blocked on GTK 4 exposing `GdkDmabufTexture`
  plane accessors (only the builder side is public through 4.22), so webkit6 falls
  back to a full CPU pixel download per frame. See `[^wk6-dmabuf]`.

## Host-side (Mere and Turnstone, not this crate)

- **Mere adapter truth and reachability.** `scrying-engine` already forwards
  navigation, input, zoom settings, cookies, and ordered script/cookie
  completions. The October 5 audit found concrete-producer claims exceeding
  reachable Inker operations; a concurrent Mere B0 source patch narrows those
  claims, pending validation. Find and host permission/auth answers retain
  unsupported defaults; downloads lose typed lifecycle details; IME caret state
  becomes diagnostics. Validate that patch, then bridge the needed typed
  requests/events in Mere. CPU/Png/overlay frames also have no Inker frame
  mapping. Source: `mere/crates/inker/engines/scrying-engine/src/{producer,translation}.rs`.
- **Turnstone host construction and owned import.** Register an optional Scry
  adapter at the same Mere revision as Inker, construct on the UI thread after
  window/device readiness, and consume the owned native frame with explicit
  producer synchronization on every paint, including reused resource epochs.
  Pelt supplies the Windows construction/import precedent at
  `mere/ports/pelt/desktop/{scrying_receipt,dx12_surface}.rs`. Profile persistence,
  routing, focus, prompt UI, and download destinations remain Turnstone policy.
- **Other platform hosts.** WKWebView needs its parent view, nonblocking run-loop
  integration, privacy consent, and Metal import. WPE needs a fixed-size and
  process-isolation policy compatible with its headless limitations. GTK CPU
  frames require a downstream upload path before being offered as composited
  browser tiles.

## Next-release and consumer gates

The October 5 Windows capture repair drains at most the two-slot WGC pool per
coalesced readiness notification, closes superseded samples, and hands off the
newest queued sample through the existing copy/fence/custody path. Both
nonblocking and explicit-wait acquisition use it. It shipped in `scrying` 0.7.2
(published 2026-10-07, tag `scrying-v0.7.2`; release notes
`docs/receipts/scry_release_readiness_20261007/release072-current-release-notes.md`).
Its scope and focused validation (five passing Windows unit tests, formatting
and whitespace checks) are recorded in the [Windows plan](2026-05-12_windows_decomposition_plan.md#capture-queue-maintenance-2026-10-05).
The 0.7.2 registry consumer receipt
(`docs/receipts/scry_release_readiness_20261007/release072-publication-README.md`)
passes RTX 4060 / DX12 Core 23/23, Capture 3/3 and a first-frame pixel control.
Still open before this repair counts as accepted, or before a Turnstone repin:
headed Windows final-static-pixel, resize/reconstruction, and two-page import
receipts. The frozen October 5 Turnstone executable used registry 0.7.1 and
therefore did not test this repair. Its cookie persistence failures and blank
final tiles remain open; the queue defect is not a proved cause of either.
Existing physical-keyboard/IME gates are unchanged by this repair.

The September 11 post-release capture-status reconciliation (`465d9a4`; the
same patch was earlier recorded as `99c0a9d`) shipped in 0.7.2 together with
the retained per-status diagnostic counters. Exact-source headed run
[37210994529](https://github.com/merely-made/wgpu-scry/actions/runs/37210994529)
supplied the first native capture results, detailed in [the diagnostic
record](2026-05-07_platform_ceilings.md#macos-capture-status-diagnostics-2026-09-11).
Still open: the counter test, and the Intel capture gate. Fresh 0.7.2
published-package Intel capture fails 9/10 in the ordinary battery and 1/2 in
the activity probe (a separately labelled foreground control also fails 9/10 and
1/2); the cause is unresolved, and the receipts attribute nothing to the
producer, WindowServer or fixture. Missing or status-only samples do not
satisfy capture acceptance.

The October 4 RADV job in that run failed at `loginctl show-session 2` with
`No session '2' known`; pixel and input steps were skipped. That was an obsolete
session-ID preflight, not a WPE product-test result. The repair enumerates the
runner user's current sessions and requires an active Wayland session owned by
that user, retaining the existing socket, no-X11, and WPE-version checks (see the
[Linux strategy](2026-05-15_phase4_strategy.md#headed-linux-preflight-repair-2026-10-05)).
It passed natively on 2026-10-07: `m4-unlocked-native-radv.log` reports a
verified active Wayland session and both `NATIVE WPE GATE PASS:
wpe_to_vulkan_roundtrip` and `NATIVE WPE GATE PASS: wpe_input`, and the 0.7.2
RADV registry trio passes.

For later producer, event-contract, or import changes, rerun the affected
platform's deterministic browser and capture battery. A shared import change
requires fresh DX12/Metal/Vulkan coverage; a claimed published combination
also needs a registry-only consumer receipt with exact source versions and
one selected host wgpu row. Keep compile, frame import, pixel, input, and
headed hardware evidence separate, as required by the canonical triplet plan,
`wgpu-graft/design_docs/2026-11-01_triplet_release_plan.md`.

Turnstone's first Windows acceptance needs a live winit/UI thread, a host-owned
wgpu-30 DX12 device/queue, matching Scry/Graft rows, explicit shared-fence
construction, isolated profile paths, and a deterministic local browser fixture.
Choose the actual composition topology first: one shared attached root per
HWND or capture-only `CompositionRoot::new_offscreen`. Attached-root native
keyboard evidence does not certify offscreen input; shared-root producers
cannot be independently reparented through today's API.

The acceptance scenario opens two separately identified browser tiles, observes
each expected page pixel through Turnstone's render target, routes pointer and
text to the selected tile without cross-talk, verifies find/zoom where the
adapter exposes them, and exercises resize/DPI, profile separation, crash
handling, and repeated fence waits across reused allocations. Record unavailable
operations visibly. Multi-pane wheel, IME/candidate placement, native popup
widgets, focus changes, and any claimed tearout/offscreen input need their own
exact-topology receipts before being included in the supported browser claim.
