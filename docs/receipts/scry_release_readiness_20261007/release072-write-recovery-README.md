# GitHub write recovery

On 2026-10-07 at approximately 17:28 UTC, normal pushes succeeded for the two pending repositories. Verified origin heads were Scry `a3c05b6121fb369882563bab579b86a8e0d94dad` and Graft `d38c14eff9c0928f8a1e79f6ab6e0a5467ff6099`. The prior HTTP 500 observations in the follow-up packet remain historical evidence.

The existing `scrying-v0.7.2` release body was updated from `release072-current-release-notes.md` and read back independently. Its normalized contents match exactly; [release072-write-recovery.json](release072-write-recovery.json) records the note hash and verified origin heads. The published source tag was not changed. The notes retain the fresh Intel failure and pending full NVIDIA trio gate.

Root dispatched [Intel session observation 37659346531](https://github.com/merely-made/wgpu-graft/actions/runs/37659346531) on exact Graft `d38c14eff9c0928f8a1e79f6ab6e0a5467ff6099`, with `observe_session=true` and `foreground_control=true`. The dispatch snapshot is recorded separately. Observation results require the completed native artifact, not successful setup or pure helper checks.

The saved NVIDIA runner remained stopped at this recovery preflight. Several other local Cargo/rustc processes were active. Starting the runner and cleaning the retained release stage were not retried after their earlier automatic approval rejections. The existing release worktree, registry consumer stage and stable-target profile caches remain owned by Root's release lane for evidence review. No new worktree, Cargo home or Cargo target was created for this recovery.
