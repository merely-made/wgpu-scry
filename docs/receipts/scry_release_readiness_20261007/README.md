# Scry release preparation, 2026-10-07

Status: proposed `scrying` 0.7.2, unpublished. Current registry release and
source manifest remain 0.7.1. No version bump, tag or upload was made.
The reviewed source is `2c3ebd24118851cf6125cfb193f55aab20e3ad67`.

The published 0.7.1 archive identifies source
`8386502915e6bad0f9d9d13cc17bb7d4bbaa769a`; the later capture fixes are
unpublished. The [packaging review](packaging-README.md) compares that registry
archive with its original Git source and assesses the compatible patch scope.
See the [draft release notes](release-notes-draft.md).

## Closed checks

The clean-source Windows package verification and all three explicit library
rows pass on Rust 1.92.0: wgpu 28, 29 and 30. The exact generated archive has
93 files and includes `src/latest_image_sample.rs`. Its normalized dependency
graph uses registry sources, including `grafting` 0.6.0. Because no version was
bumped, this archive still names 0.7.1 and cannot be uploaded over the existing
release. It is a reversible source/package qualification receipt.

The [independent audit](root-package-audit.json) checks all five completed
commands, package VCS identity, all 88 Rust files against Git after CRLF
normalization, and preservation of the eight concurrent dirty documents.
Current-source matrix, Mac and Linux CI also pass. Those current CI jobs do not
replace a current Mac/Linux Rust 1.92 check or native hardware acceptance.

Turnstone's separately recorded Windows Scry controls pass two-page input and
same-profile process restart on this source. They retain their own consumer
executable identity in
[`Turnstone's family receipt`](https://github.com/merely-made/turnstone/blob/e00869cbcc5d8e58bd2ef5dbb30c47a03d48c023/docs/receipts/browser_family_20261007/README.md).

## Remaining release gates

The [fresh hardware observation](headed-jobs.json) confirms run
[37555489592](https://github.com/merely-made/wgpu-scry/actions/runs/37555489592)
on prior experimental harness source `6143ed74`: RADV passes, Intel and M4
fail, and NVIDIA remains queued. Main `2c3ebd24` restores the capture harness;
it has no passing replacement native run. The failed Mac observations report
a hidden fixture, stopped animation and insufficient capture cadence. They do
not establish a locked session, driver or importer cause. Full details remain
in the preserved [Mac investigation](../mac_sample_retention_20261006/README.md).

Both configured Mac SSH routes refuse connections in the
[read-only session observation](mac-session-observation.json), so this audit
cannot verify their desktop/session state. No session or runner settings were
changed, and the existing hardware run was not cancelled or redispatched.
The user was asked for the M4 desktop's logged-in/unlocked state; no answer
is inferred from silence.

Before publishing: obtain a visibly advancing Mac fixture and passing original
capture/resize batteries on the final source; execute the standalone NVIDIA
battery; run the full current Rust 1.92 Mac/Linux feature matrix; integrate
reviewed release documentation; then bump 0.7.2 and verify the final package.
A fresh registry-only consumer receipt follows publication of that version.

## Ownership

The clean packaging worktree was used because the primary README and seven
other audit documents contain concurrent edits. Their exact bytes remain
preserved. The [cleanup record](packaging-cleanup.json) confirms that the owned
worktree was removed. The stable reusable
`C:/t/cargo-targets/wgpu-scry` cache remains. No isolated Cargo home was created.
The installed Rust 1.92.0 toolchain remains available for the declared-floor gate.
This preparation publishes only its own receipt and draft notes.
