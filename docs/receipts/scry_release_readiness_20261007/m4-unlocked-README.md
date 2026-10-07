# Scry release qualification after desktop availability

This continuation preserves the earlier preparation packet at `4771072a6827695dfaba9db104cd48b87e6cd543`. The qualified overlay is integrated with source version `scrying 0.7.2`; registry publication is pending.

## Completed qualification on the unchanged source

- Apple M4: original native battery **10/10**, separate capture activity diagnostic **2/2**. Ordinary capture delivered five frames; resize capture delivered 805 frames across all four required sizes. The diagnostic observed a visible page and advancing animation.
- Intel iMac: the original attempt retained its **9/10** and **1/2** failures with a hidden page and zero animation frames. After the user reported the desktop unlocked, an Intel-only second attempt passed **10/10** and **2/2**. These observations do not establish the cause of the earlier failure.
- ThinkPad RADV: the native WPE construction, Vulkan pixel, and input gates passed. This is native evidence, not a skipped hosted check.
- Local Windows NVIDIA RTX 4060 / DX12: all **22 Core modes** and **2 Capture modes** passed with the same source and frozen executable. Capture modes check import and sizes; they do not assert pixel colors.
- Rust **1.92**: all **12 required jobs** passed, including Windows/macOS/Linux with wgpu 28/29/30 and the three Linux engine families. These are compile receipts, not native hardware receipts.

The hardware Actions workflow includes a cancelled, unassigned NVIDIA job. Its overall status is not an all-host success. The separately recorded local NVIDIA results supply the Windows battery evidence. The Intel-only rerun preserved the completed M4 and RADV results.

## Windows startup pixel investigation

Two supplemental, unchanged readback controls failed and remain in the packet. The scripted fixture does not match the checker’s fixed background. The correct normal-page `--probe-only` control also failed: all five sampled BGRA pixels were zero in generation 1. Neither result is counted as a pixel pass.

The source review found that `wait_for_render_tick` submits a Promise to `ExecuteScript` and discards its evaluation result. It does not acknowledge that the two requested animation callbacks completed. The navigation, fixture, and readback code is unchanged from the published 0.7.1 source. This identifies a missing wait guarantee; it does not by itself identify the cause of the blank capture or prove an importer defect.

A bounded implementation lane separated navigation completion from an explicit, timeout-configurable CDP Promise wait. Its frozen candidate passed **23 Core modes**, **2 Capture modes**, the reply-validation regression, and Rust **1.92** Windows checks for wgpu **28/29/30**. The added maintained Core mode verifies navigation while the document is hidden and subsequent visibility restoration.

The same normal-page, first-frame pixel assertion still failed on that candidate. Unlike the baseline blank frame, it captured nonzero pixels: both top corners matched the expected background exactly, while the bottom corners and center contained other colors. DOM geometry and sample-location qualification is pending. An animation callback acknowledgement does not by itself guarantee a captured compositor paint, and this packet does not count the candidate pixel result as a pass.

The DOM diagnostic confirmed a **210×130 CSS viewport** at **DPR 2** for the 420×260 capture. Both bottom sample points lie inside the textarea, whose background is `rgb(15,23,32)`. The white bottom-right sample's native form/scrollbar origin is not established, but that point is not bare page background. The original fixture and failed controls remain unchanged and retained.

The maintained `--pixel-test` uses a separate fixture with reserved background corners and a contrasting opaque center. It passed on **generation 1**, using the same single acquisition, five sample locations, and original ±6 corner assertion: all four corners were exactly BGRA `[42,32,23,255]`, and the center exactly `[37,71,211,255]`. The final executable also passed **Core 23/23** and **Capture 3/3**, including this pixel mode. Its SHA-256 is `f6be03e348243c526f2248351b2cc2e3ad13778f419701b0625b9a94951f3af9`.

The final nine-file overlay is integrated with a version-only 0.7.2 manifest/lock change. Its library and dependency graph match the parser/MSRV-qualified candidate. Exact 0.7.2 package verification and publication are next; fresh registry-only consumer acceptance follows publication.

## Custody and retained output

`m4-unlocked-msrv-hashes.json` binds 19 artifacts. `m4-unlocked-windows-hashes.json` binds 28 artifacts and the Windows source archive. The root independently verified both indices without a mismatch. Raw native logs, earlier failures, exact source identities, and executable hashes are retained.

The first owned Windows worktree was removed. Its marker-owned runtime profiles remain under the stable `C:/t/cargo-targets/wgpu-scry/native-smoke-runtime` for the failure review and follow-up lane; they are generated output, not published artifacts. Eight pre-existing dirty documentation files in the primary checkout were preserved byte for byte.

The user also reported the Kubuntu Surface unlocked. Its SSH alias `s-pc` did not resolve; a usable SSH address is still requested. The Surface is supplemental and is not substituted for an existing hardware gate.
