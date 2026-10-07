# Published-package Intel foreground control

Run [37639574080](https://github.com/merely-made/wgpu-graft/actions/runs/37639574080), job 112854631296, uses wrapper `0e491151d6943d04959fe0ad31477602806ed9df`, the unchanged published Scry fixture `4d8d1d3f8dd450b712960c90b74263a45b46e35b`, and the registry helper `e8ffee2d6b680154cae645d54a340116f08acb5d`.

All four phases fail: ordinary 9/10, activity 1/2, foreground ordinary 9/10, and foreground activity 1/2. Base capture acquires three frames against the original five-frame minimum. Resize passes in every phase. The two controlled phases attempt one activation per exact live owned app process (10 and 2 attempts); every request exits zero, but host focus remains false. Activity samples remain hidden with zero animation callbacks and zero CSS animation time while timers and resize advance.

These results establish that the activation request did not restore an active page. They do not establish the session cause or a capture-custody defect. Original failures, thresholds, timeouts, fixture source, registry dependencies and executable identities remain preserved. Final custody received/consumed counters are unavailable in these logs.

Root independently verified all seven files in the agent hash index, the four failed phase totals, the raw activity and activation markers, and all eight unrelated primary-document hashes. The separate packet index includes this report and the original agent index. Neither earlier negative packet was rewritten.
