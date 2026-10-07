from pathlib import Path
import datetime, hashlib, json, re, subprocess, zipfile

P = Path('C:/Users/mark_/Code/repos/wgpu-scry')
W = Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release')
O = P / 'docs/receipts/scry_release_readiness_20261007'
PREFIX = 'm4-unlocked-windows-'
def load(name): return json.loads((O/(PREFIX+name)).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, obj):
    with (O/(PREFIX+name)).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,indent=2); f.write('\n')
inputs = load('inputs.json'); before = load('initial-guards.json'); after = load('source-after.json'); exe = load('executable.json')
assert after['source_commit'] == before['source_commit'] == inputs['source_commit']
assert not after['changed_inputs'] and not after['tracked_status']
assert after['executable_sha256'] == exe['sha256'] == sha(Path(exe['path']))
assert all(sha(W/x['path']) == x['sha256'] for x in inputs['inputs'])
with zipfile.ZipFile(O/inputs['archive']) as z:
    assert z.namelist() == [x['path'] for x in inputs['inputs']]
    assert all(hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256'] for x in inputs['inputs'])
assert sha(O/inputs['archive']) == inputs['archive_sha256']
dirty = [{'path':x['path'],'sha256_before':x['sha256'],'sha256_after':sha(P/x['path']),'unchanged':sha(P/x['path'])==x['sha256']} for x in before['dirty_docs_before']]
assert all(x['unchanged'] for x in dirty)
gates=[]
for label,count in [('core',22),('capture',2)]:
    record=load(label+'.result.json')
    text=(O/(PREFIX+label+'.stdout.log')).read_text(encoding='utf-8-sig')
    error=(O/(PREFIX+label+'.stderr.log')).read_text(encoding='utf-8-sig')
    modes=[]
    for match in re.finditer(r'==> (--[a-z-]+)\s*\n([\s\S]*?)(?=\n==> |\Z)',text):
        mode,body=match.groups()
        observed=[x for x in record['native_process_observations'] if x['command'][-1]==mode]
        exits=[x.get('actual_exit_code') for x in observed]
        # The unmodified runner prints PASS only after WaitForExit succeeds and actual ExitCode==0.
        passed='  -> PASS' in body and '  -> FAIL' not in body
        modes.append({'mode':mode,'script_native_exit_code':0 if passed else None,'exit_evidence':'Existing Invoke-DemoMode native ExitCode check; independently held child handles when observed','independent_observations':observed,'timed_out':'timed out' in body,'passed':passed,'reported_assertions':[s for s in body.splitlines() if 'PASS' in s or 'scale-test: captured' in s or 'capture-test: captured' in s], 'reported_adapter_names':re.findall(r'wgpu adapter: (.+)',body),'reported_backends':re.findall(r'wgpu backend: (.+)',body)})
        assert passed and not ('timed out' in body) and all(x==0 for x in exits)
        assert modes[-1]['reported_adapter_names']==['NVIDIA GeForce RTX 4060 Laptop GPU']
        assert modes[-1]['reported_backends']==['Dx12']
    assert record['actual_exit_code']==0 and len(modes)==count and f'passed: {count} / {count}' in text and 'all PASS' in text
    assert record['executable_sha256']==exe['sha256']
    gates.append({'suite':label,'actual_script_exit_code':record['actual_exit_code'],'modes':modes,'stderr_preserved':True,'stderr_bytes':len(error.encode('utf-8')),'per_mode_deadline_seconds':90})
pixel_controls=[]
for label in ['pixels','probe-pixels']:
    pixel = load(label+'.result.json')
    text=(O/(PREFIX+label+'.stdout.log')).read_text(encoding='utf-8-sig')
    assert not pixel['timed_out'] and pixel['executable_sha256']==exe['sha256']
    expected=re.search(r'expected background BGRA=\((\d+),(\d+),(\d+),255\)',text)
    assert expected
    bgra=list(map(int,expected.groups()))+[255]
    samples={name:[int(v.strip()) for v in values.split(',')] for name,values in re.findall(r'(tl|tr|bl|br|center)=BGRA\[([^\]]+)\]',text)}
    assert set(samples)=={'tl','tr','bl','br','center'}
    corners=all(all(abs(samples[c][i]-bgra[i])<=6 for i in range(3)) for c in ['tl','tr','bl','br'])
    alpha=any(s[3]>0 for s in samples.values())
    assert f'corner pixels match background within ±6: {str(corners).lower()}' in text
    assert 'wgpu adapter: NVIDIA GeForce RTX 4060 Laptop GPU' in text and 'wgpu backend: Dx12' in text
    pixel_controls.append({'label':label,'command':pixel['command'],'actual_exit_code':pixel['actual_exit_code'],'timed_out':pixel['timed_out'],'expected_bgra':bgra,'samples':samples,'corner_rgb_tolerance':6,'corners_match':corners,'any_nonzero_alpha':alpha,'passed':pixel['actual_exit_code']==0 and corners and alpha,'native_process_observations':pixel.get('native_process_observations',[{'pid':pixel['owned_pid'],'actual_exit_code':pixel['actual_exit_code'],'observed_priority':pixel['observed_priority']}]) if label=='probe-pixels' else pixel['native_process_observations'],'scope':'Existing startup imported-GPU readback at 420x260 generation1; distinct from Capture/scale dimensions. Scripted scroll/input fixture differs from normal overflow:hidden probe-only fixture. Preserve both actual failures; normal probe-only all-zero samples are a genuine initial readback failure, cause not proven.'})
runtime=Path(after['runtime_cache'])
runtime_inventory=[{'path':str(f.relative_to(runtime)).replace('\\','/'),'bytes':f.stat().st_size,'sha256':sha(f)} for f in sorted(runtime.rglob('*')) if f.is_file()]
save('native-summary.json', {'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':inputs['source_commit'],'source_tree':inputs['source_tree'],'toolchain':inputs['rustc'],'source_inputs_verified':len(inputs['inputs']),'archive_verified':True,'exact_executable':exe,'build_actual_exit_code':load('build.result.json')['actual_exit_code'],'core_capture':gates,'startup_pixel_validation':pixel_controls,'startup_pixels_all_pass':all(x['passed'] for x in pixel_controls),'qualification_scope':'Core22 and Capture2 PASS. Both additional startup pixel controls FAIL; pixel correctness remains open. No claim of resized frame pixels or real IME/user interaction.','adapter':'NVIDIA GeForce RTX 4060 Laptop GPU','driver_version_observed':'32.0.16.1088','explicit_backend_environment':'dx12','native_backend_observed':'Dx12','primary_dirty_docs':dirty,'runtime_cache':str(runtime),'runtime_inventory':runtime_inventory,'runtime_profiles_retained_for_review':True,'source_changes':[],'publication':False})
print('AUDITED Core22 Capture2 PASS, startup pixels FAIL; source and executable unchanged; eight primary dirty docs preserved')
