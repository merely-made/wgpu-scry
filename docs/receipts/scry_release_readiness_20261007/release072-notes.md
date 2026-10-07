# scrying 0.7.2

- WebView2/WGC drains coalesced capture notifications and retains the newest queued frame through the existing copy/fence path.
- ScreenCaptureKit preserves a pending image when later callbacks contain only status information, with an ownership regression and retained diagnostic counters.
- WPE refuses construction on a worker thread before native initialization. Native integration gates construct on the process main thread.
- WebView2 navigation completes independently of animation callbacks. The new explicit `wait_for_render_tick(timeout)` awaits and checks the two callbacks' CDP result; hidden navigation remains usable. Callback completion does not guarantee a captured compositor paint.
- Windows' maintained native battery includes hidden-navigation and first-frame pixel controls. The pixel fixture reserves background corners across DPI scales and checks a contrasting opaque center.

Rust 1.92 and the wgpu 28/29/30 choices are retained. A Windows-only JSON dependency validates the CDP result. Existing dependency versions are preserved.

Native qualification records Apple M4 and Intel capture/resize, ThinkPad RADV WPE pixels/input, and RTX 4060 DX12 Core 23/23 plus Capture 3/3. Earlier failed controls are retained and are not counted as passes. Exact-package and post-publication registry-only consumer receipts are recorded separately.
