# scrying 0.7.2

- WebView2/WGC drains coalesced capture notifications and retains the newest queued frame through the existing copy/fence path.
- ScreenCaptureKit preserves a pending image when later callbacks contain only status information, with an ownership regression and retained diagnostic counters.
- WPE refuses construction on a worker thread before native initialization. Native integration gates construct on the process main thread.
- WebView2 navigation completes independently of animation callbacks. The new explicit `wait_for_render_tick(timeout)` awaits and checks the two callbacks' CDP result; hidden navigation remains usable. Callback completion does not guarantee a captured compositor paint.
- Windows' maintained native battery includes hidden-navigation and first-frame pixel controls. The pixel fixture reserves background corners across DPI scales and checks a contrasting opaque center.

Rust 1.92 and the wgpu 28/29/30 choices are retained. A Windows-only JSON dependency validates the CDP result. Existing dependency versions are preserved.

Native qualification records Apple M4 and Intel capture/resize, ThinkPad RADV WPE pixels/input, and RTX 4060 DX12 Core 23/23 plus Capture 3/3. Earlier failed controls are retained and are not counted as passes. Exact-package and post-publication registry-only consumer receipts are recorded separately.

Post-publication registry consumers pass RTX 4060/DX12 Core 23/23 and Capture 3/3, the full M4 trio battery (Scry 10/10, Weld 17 passes), and the RADV trio battery (both WPE gates, Weld 16 passes with its documented crash-test skip). The registry archive exactly matches the verified package, and the fresh twelve-job Rust 1.92 matrix passes.

Fresh Intel registry capture remains unqualified. The latest passive-session diagnostic fails 8/10 ordinary, 0/2 activity, 8/10 foreground-controlled ordinary and 1/2 foreground-controlled activity. Base capture acquires two or three frames against five required; three phases also miss the unchanged three-frame minimum at one resize size. Activity stays hidden with zero animation callbacks and zero CSS animation time. The observer cannot see a GUI session, window list or the exact owned app despite matching runner/console UIDs. Physical lock state and the cause remain unknown. The next controlled check is runner admission into the logged-in desktop session. A green four-host trio workflow remains open; the existing NVIDIA Actions runner is stopped.

[Published-package and consumer receipts](https://github.com/merely-made/wgpu-scry/blob/main/docs/receipts/scry_release_readiness_20261007/release072-publication-README.md) preserve both successful and failed controls.
