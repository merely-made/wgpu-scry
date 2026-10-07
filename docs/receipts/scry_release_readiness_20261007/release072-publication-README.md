# Scry 0.7.2 publication and registry consumer continuation

`scrying` 0.7.2 is published from clean source commit
`4d8d1d3f8dd450b712960c90b74263a45b46e35b`, with annotated tag
[`scrying-v0.7.2`](https://github.com/merely-made/wgpu-scry/releases/tag/scrying-v0.7.2).
The registry records publication at 2026-10-07 13:42:15 UTC. Actual publish
exit is zero. The downloaded registry package is exactly the qualified
package and dry-run archive: 338,664 bytes, 93 members, SHA-256
`74486b58a87ac1ea36ba33e24ffaf513570845bcd1d1c099cc872923dc83d740`.
Root independently checked its clean VCS identity, packaged Rust sources,
registry Graft dependency and normalized manifest. See
`release072-publish-result.json`, `release072-registry-metadata.json` and
`release072-package-root-audit.json`.

The exact source passes the fresh twelve-job Rust 1.92 declared-floor matrix
[37629684987](https://github.com/merely-made/wgpu-scry/actions/runs/37629684987).
The source-phase native receipts and retained earlier failures are described
in `m4-unlocked-README.md`; that historical snapshot remains unchanged.

## Fresh Windows registry consumer

The staged standalone consumer selects exact registry releases `grafting`
0.6.0, `scrying` 0.7.2 and `welding` 0.14.1. Its resolved dependencies are
registry-only, with one wgpu 30.0.1 and no Git/path/patch overrides. Demo and
test inputs come from exact published source 4d8; only package selection is
rewritten in the copied test script. The timeout remains 90 seconds per mode.
The downloaded package checksum also matches the Cargo.lock checksum.

The BelowNormal, `-j1`, Rust 1.97.1 build exits zero. Its executable SHA-256 is
`09727985de18cf1d73a270cbdff66596647ad31ed0581117890063bac1b2ad87`.
On the local NVIDIA RTX 4060 Laptop GPU through DX12, actual native exits are
zero for Core 23/23, Capture 3/3 and a separate first-frame pixel control.
No command timed out. All four background corners are exactly
BGRA [42,32,23,255], and the opaque center is [37,71,211,255]. These results
qualify the Scry Windows consumer, not native execution of all three engines.
The `release072-registry-win-*` packet preserves inputs, registry archives,
metadata, lock, executable identity, raw logs and observed process exits.

## Four-host triplet proof remains open

Fresh registry workflow
[37631036166](https://github.com/merely-made/wgpu-graft/actions/runs/37631036166)
uses wrapper `dcab3700cb8bbf208d1c4206433275c2c97cd715`, Graft fixture
`816f3e7857afee863200e1c25b300c43b1532aae`, Scry source 4d8 and Weld fixture
`c7b7b4c52138643e22580a918542e8e036a0b24a`. M4, Intel and RADV all failed
compilation of `rsa` 0.10.0-rc.18 against freshly resolved `pkcs1`
0.8.0-rc.5, before native execution. The Graft fixture lock uses rc.4.
The three full job logs retain the eight E0107 errors each. The unassigned
NVIDIA job was cancelled after the assigned jobs completed. This run does
not establish current Mac/Linux registry-native success or a green triplet
workflow. Fixture reproducibility is being corrected separately.

Servo ordering/pixel, foreign accessibility and combined application gates
remain separate from this Scry publication and its native qualification.

## Retained generated data

Automatic approval review rejected removal of the archived owned registry
staging directory and its detached worktree, reporting only "blocked by
policy." Neither deletion executed, and no alternate cleanup was attempted.
`C:/Users/mark_/Code/worktrees/wgpu-scry-release` remains owned by this release
lane for the preserved registry consumer. The stable reusable build target
is `C:/t/cargo-targets/wgpu-scry`; marker-owned native profile caches remain
with their failure/proof review context. No isolated Cargo home was created.
The eight unrelated primary-checkout Mac audit documents remain unstaged.
