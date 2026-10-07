# scrying 0.7.2 candidate notes

Unpublished draft for source `2c3ebd24118851cf6125cfb193f55aab20e3ad67`.
The manifest remains 0.7.1. No tag or registry upload has occurred.

- WebView2 capture drains the bounded queued frames after a coalesced readiness
  notification and retains the newest sample through the existing copy/fence
  path. Both nonblocking and explicit-wait acquisition use the repair.
- ScreenCaptureKit retains a pending image when subsequent callbacks contain
  only status information. Capture diagnostics retain delivery/status counts,
  and the ownership regression verifies that the image survives until acquired.
- WPE construction refuses worker-thread initialization before touching native
  state. Native WPE acceptance runs on the process main thread; headed Linux
  preflight discovers the runner's current active session.

These changes retain the published API and the wgpu 28/29/30 feature choices.
Windows Turnstone input/profile-restart controls and RADV native pixel/input
checks pass in their recorded scopes. Current compile/test CI passes.

The candidate is not release-qualified: the last Mac native capture run failed
while the fixture reported a hidden page and a stopped animation. The restored
capture harness has no passing replacement native receipt. The standalone
NVIDIA battery remains queued. Windows Rust 1.92 wgpu 28/29/30 and exact-source
package verification pass; current Mac/Linux declared-floor checks remain open.
Registry-only consumer acceptance must follow
publication of the selected version. Those outcomes must be reflected in final
release notes before publication.
