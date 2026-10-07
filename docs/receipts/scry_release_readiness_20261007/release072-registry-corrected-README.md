# Corrected registry triplet continuation

Fresh run [37633624184](https://github.com/merely-made/wgpu-graft/actions/runs/37633624184)
binds wrapper `e8ffee2d6b680154cae645d54a340116f08acb5d`. It keeps the exact
registry versions Graft 0.6.0, Scry 0.7.2 and Weld 0.14.1 and the original
immutable fixtures: Graft `816f3e7857afee863200e1c25b300c43b1532aae`, Scry
`4d8d1d3f8dd450b712960c90b74263a45b46e35b`, Weld
`c7b7b4c52138643e22580a918542e8e036a0b24a`.

The wrapper adds an exact registry PKCS1 rc.4 constraint only to the copied
Servo fixture. Prior passing lock/native evidence and the official RSA/PKCS1
source delta are committed in Graft's
`docs/receipts/registry_rsa_reconciliation_20261007/`. The correction does not
change a published package, test assertion or timeout. The failed previous
run and its three raw negative logs remain frozen in the earlier publication
packet, rather than being replaced by this attempt.

Intel job 112834014127 completes with failure after Graft passes: the
original Scry battery is 9/10. Base capture receives three frames in 30
seconds against the original five-frame minimum. Its host window reports
visible/unminimized but unfocused; ScreenCaptureKit reports three Complete
and 1,741 Idle callbacks. Resize passes with twelve acquired frames and
thirteen Complete callbacks, which are distinct counters. The full raw log
and job metadata are retained. The preceding source-native Intel success
remains valid historical evidence, but does not close this new registry
failure. Unlock state does not establish DOM visibility or advancing animation.

M4 job 112834014591 completes with success. Its raw native evidence reports
Graft GPU import, 82 frames, changed pixels and a 960x640 resize; Scry 10/10
with five base frames and 427 resize frames across four sizes; and Weld
17 pass, zero live/skip/fail. Registry metadata selects exact published trio
versions and one wgpu per consumer (Graft's historical Servo fixture 29.0.4,
Scry and Weld 30.0.1). Raw job metadata and logs are retained.

RADV job 112834014753 completes with success. Graft reports GPU import,
15 frames, changed pixels and a 960x640 resize. Both required WPE native
gates pass without skips, including 64x64 imported center pixels and input,
messages and cookies. Weld reports 16 pass, zero live/fail and one explicitly
configured crash-test skip inherited from the existing workflow. This does
not claim Linux crash recovery.

The root audit archives all three completed job artifacts and independently
checks all nine consumer graphs. Each selects exact published trio releases
and one wgpu. Scry/Weld have no external non-registry dependencies. Graft
retains the historical fixture's 57 allowed Servo/glslopt Git packages;
these are distinct from the three registry supplier packages. Metadata member
hashes and downloaded artifact identities are in
`release072-registry-corrected-audit.json`.

The workflow was cancelled only after all three assigned jobs completed,
because NVIDIA job 112834014723 remained unassigned. Neither this partially
passing run nor the separately passing local Windows Scry consumer establishes
the required green four-host triplet workflow. Intel capture cadence and the
NVIDIA Actions runner remain open.
