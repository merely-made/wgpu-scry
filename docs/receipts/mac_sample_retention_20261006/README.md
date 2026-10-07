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
