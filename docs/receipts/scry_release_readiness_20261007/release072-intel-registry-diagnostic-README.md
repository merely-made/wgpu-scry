# Intel registry capture negative control

[Run 37637005234](https://github.com/merely-made/wgpu-graft/actions/runs/37637005234)
uses focused diagnostic wrapper `d6c119f2b41cf5e81c99157166885c7f3800ab67`,
immutable helper e8ffee2, exact source 4d8 and the published trio registry
dependencies. Setup, registry identity and build checks pass. The unchanged
ordinary ten-mode battery fails 9/10; the separately instrumented two-mode
diagnosis fails 1/2. Both failures are the original five-frame base capture
requirement, with only three acquired frames and three Complete callbacks.
Resize passes with twelve and thirteen acquired frames, respectively.

The activity probe reports hidden DOM visibility, zero animation-frame
callbacks and zero CSS animation current time, although animation state is
running. Timer and resize callbacks continue. Host-window reports remain
visible, unminimized and unfocused; SCK emits many Idle callbacks without
source-dimension or configuration-revision mismatches. These observations
establish inactive page animation in this context. They do not establish the
focus, session, driver or capture-custody cause. Activity instrumentation
cannot substitute for the ordinary test fixture.

The artifact binds the exact registry source VCS identities, one wgpu
30.0.1, executable/signature identity before and after both batteries and
copied demo Rust inputs equal to published source 4d8. The raw executable
and signed app are each unchanged between the ordinary and diagnostic runs.
The artifact's 24 members are hashed separately; this packet retains the
full job log, metadata, result, archive and root dispatch snapshot.

The next separately labelled control performs one activation of the exact
owned demo bundle per mode, then repeats the ordinary and activity batteries
without changing Rust/library sources, the five-frame/30-second requirement
or 90-second wall cap. This negative packet remains immutable.
