# ScreenCaptureKit image retention

The callback previously replaced the one pending sample with every Screen
sample, including status-only samples without a CVImageBuffer. A Complete
sample followed by Idle before the host poll therefore lost its pixels.
The repaired callback retains only image-bearing samples for the pending slot.
Every Screen callback still contributes to delivery/status diagnostics; samples
without images are counted at callback receipt instead of consumer dequeue.

The portable regression exercises that actual slot update rule with owned
objects: a hundred status-only callbacks preserve the image without dropping
its custody; a newer image releases the older one and leaves exactly one image
for the consumer. The Mac native hardware workflow runs these tests before its
unchanged five-frame base / three-frame-per-resize assertions.

## Prior native evidence

Scry run 37533331164 used checkout 97b7579ca5e2818aff08a83b2f66d2ea4a82e77d.
The final checkout SHA is present in each job's git log -1 output.

- Intel job 112507945134: base failed with four acquired frames; callback
  diagnostics recorded 46 Complete and 1,791 Idle samples. Configuration,
  source-dimension and crop rejection counters were zero. Its resize run
  passed with 812 frames. These facts support fixing status-only overwrite;
  they do not yet qualify the repaired native run.
- M4 job 112507945699: base failed with only three Complete callbacks and no
  Idle callbacks. Resize failed with eleven Complete callbacks and only two
  at the startup portrait size. The retention defect does not explain missing
  callbacks on this host; that cause remains open.
- RADV job 112507945788 passed worker-constructor refusal, native pixels, and
  page input. NVIDIA job 112507945474 remained queued at this investigation.
- Weld run 37530088110 at b5cf043 passed RADV job 112496930621, M4 job
  112496930745, and Intel job 112496930751. NVIDIA job 112496930340 remained
  queued. These results do not qualify a new Scry source revision.

## Qualification and remaining gates

Local Rust 1.97.1 Cargo library tests passed 2/2
(`cargo-portable-tests.log`), and a standalone compilation of the same helper
passed 2/2 (`portable-tests.log`). Restoring the former overwrite rule in
`status_only_overwrite_control.rs` fails the status-only custody test, releasing
the pending image before the consumer acquires it
(`overwrite-control-tests.log`). The temporary standalone test executables and
PDBs were removed after these logs were recorded. The existing Cargo target is
retained for ordinary builds.

Root review accepted this bounded source fix and portable regression. Local
qualification is complete; an exact committed-source Mac rerun and current
native receipts across the four hosts are still required before release.
M4 cadence, NVIDIA runner availability, version/package contents, the published
wgpu feature rows and Rust 1.92 promise, and a registry-only downstream consumer
remain release gates. No version was changed, no tag was created, and no package
was published by this investigation.

Only the existing C:/t/cargo-targets/wgpu-scry build cache is used locally.
No isolated Cargo home or worktree was created. Local Windows tests qualify the
portable rule; they do not compile or execute the Mac FFI callback.

A new exact-source hardware workflow dispatch is approved. Its
`cancel-in-progress: true` concurrency rule is expected to cancel the previous
Scry run, including its still-queued NVIDIA job. That cancellation does not
provide NVIDIA qualification.

## Reviewed fix: exact-source hardware run

The reviewed fix was committed and pushed as
`f952abc47d3d12b15530a958277df76f2e8eac2b`. GitHub rejects a commit SHA as a
workflow-dispatch ref, so remote `main` was verified equal to that SHA before
dispatching its branch ref. Run **37553214645** records that exact `headSha`,
and the Intel/M4 job logs also record that actual final checkout SHA.
The previous run 37533331164 was cancelled by workflow concurrency as expected.

- RADV job 112573348029 passed on this revision.
- Intel job 112573348255 passed the two ownership tests and size unit test,
  then failed native cadence. Base delivered three Complete callbacks and
  acquired all three, alongside 1,745 Idle callbacks. Resize delivered and
  acquired fourteen Complete frames but had only two at startup 1024x1536.
  Configuration, dimensions and crop rejection counters remained zero.
- M4 job 112573348324 passed ownership/size unit tests and the five-frame base
  capture, then failed resize with two startup 1024x1536 frames. All eleven
  Complete callbacks were acquired; there were no Idle callbacks and no
  configuration, dimensions or crop rejections.
- NVIDIA job 112573348251 remains queued in the recorded snapshot.

The retention regression is locally and natively validated, and every Complete
callback in these failed runs reached the consumer. The broader Mac cadence
gate remains open. Fixture animation/visibility, host activity and callback
delivery require a separate diagnostic receipt; this run does not establish a
driver or importer fault.

## Separate activity diagnosis

The next bounded diagnostic slice adds `--capture-activity`. Only that explicit
flag selects `scrying-test://capture?activity=1`, which injects page observers.
The default capture URL and its original HTML/CSS remain unchanged. The compiled
`fixture-bytes-guard.rs` compares default fixture bytes against f952abc; its log
records a pass. `verify-fixture.cjs` also parses the opt-in JavaScript without
executing it. The temporary guard executable/PDB were removed.

The hardware workflow runs the ordinary ten-mode native battery first. A
separate `CAPTURE_ACTIVITY=1` script run then executes only the two capture
modes, even if the earlier battery fails. The workflow retains that original
failure; a diagnostic green result cannot close the uninstrumented gate.
The script now exits immediately when a rebuild fails, preventing an older
leftover executable from serving as an exact-source qualification receipt.

Both paths add one-second host delivery/acquisition/window counters and
Occluded event logs; capture-mode events are drained in the host polling tick
as well as window events. Those host observations can affect scheduling too.
The opt-in fixture additionally reports page visibility/focus, viewport, CSS
animation clock/background, timer ticks and animation-frame callback counts.
Nothing changes the capture dimensions, deadlines, resize schedules or minimum
frame assertions. Native diagnosis must distinguish observer behavior from
evidence about the underlying scarcity.

## Exact activity diagnosis and headed focus trial

Diagnostic revision `550b9fb86c272f6ad9949734023288dd0eb1b90b` was dispatched
as run **37554112839**; actual checkout SHAs are present in its native job logs.
RADV 112576238120 passed and NVIDIA 112576237940 remained queued.
Intel 112576238318 and M4 112576238332 compiled and passed the portable custody
and capture-size tests, but their ordinary and diagnostic battery steps failed.

Intel ordinary base acquired three Complete frames, and ordinary resize acquired
eleven, with startup only two versus the required three. Its opt-in base also
failed at three; opt-in resize passed with twelve. M4 ordinary and opt-in bases
passed at five, while both resize modes failed at eleven total and only two
startup frames. These opt-in passes do not replace the ordinary failures.

On both hosts, every reported opt-in page observation was `visibility: hidden`,
`focused: false`, `animationFrames: 0`, unchanged blue background and CSS
animation `currentTime: 0`, even though timer ticks advanced. Host counters
reported a visible, non-minimized, unfocused window. Complete callbacks reached
the consumer; the fixture's animation was not advancing. This is evidence of
page suspension, not evidence of driver or importer failure.

The demo does not invoke the producer's `set_visible`; the library's Mac method
maps to `WKWebView.setHidden(!visible)`, and its constructor attaches the view
with `parent_view.addSubview`. The reviewed bounded host trial makes
`--capture-test` explicitly use Regular AppKit activation and requests
`focus_window()` once after successful window/show/producer/render setup.
That winit Mac method activates the application and makes the visible window
key/front. No library producer, fixture bytes, deadlines or thresholds change.
Ordinary/headless modes retain their policy; there is no refocus loop or forced
paint. The exact next native run must show original acceptance and opt-in
visible-page/advancing-animation evidence before this trial closes the gate.
