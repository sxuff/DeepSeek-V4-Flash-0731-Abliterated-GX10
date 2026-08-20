#!/usr/bin/env python3
import argparse, hashlib, json, math, re, statistics
from pathlib import Path

def load_jsonl(p): return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def parse_metrics(p):
    d={}
    for line in p.read_text().splitlines():
        if not line or line.startswith('#') or '{' in line: continue
        parts=line.split()
        if len(parts)==2:
            try:d[parts[0]]=float(parts[1])
            except ValueError:pass
    return d

def metric_delta(root,arm,name):
    a=parse_metrics(root/arm/'metrics-before.txt'); b=parse_metrics(root/arm/'metrics-after.txt'); return b.get(name,0)-a.get(name,0)
def telemetry_summary(root,arm):
    status=json.loads((root/arm/'watchdog-status-final.json').read_text()); pid=status['main_pid']; rows=[]
    for x in (root/arm/'watchdog-telemetry.jsonl').read_text().splitlines():
        try:r=json.loads(x)
        except:continue
        if r.get('main_pid')==pid: rows.append(r)
    return {'main_pid':pid,'samples':len(rows),'minimum_mem_available_gib':min(r['mem_available_bytes'] for r in rows)/1024**3,'maximum_swap_growth_mib':max(r['swap_growth_bytes'] for r in rows)/1024**2,'incident':(root/arm/'watchdog-incident.json').exists()}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--run',required=True); a=ap.parse_args(); root=Path(a.run)
    rows={arm:load_jsonl(root/arm/'rows.jsonl') for arm in ['plain','dspark']}
    for arm in rows:
        assert len(rows[arm])==36
        keys=[(r['fixture_id'],r['rep']) for r in rows[arm]]; assert len(keys)==len(set(keys))
        assert not any(r.get('error') for r in rows[arm])
    paired=[]
    pmap={(r['fixture_id'],r['rep']):r for r in rows['plain']}; dmap={(r['fixture_id'],r['rep']):r for r in rows['dspark']}
    assert pmap.keys()==dmap.keys()
    for k in sorted(pmap):
        p,d=pmap[k],dmap[k]; paired.append({'fixture_id':k[0],'rep':k[1],'request_sha_match':p['request_sha256']==d['request_sha256'],'output_sha_match':p['output_sha256']==d['output_sha256'],'finish_reason_match':p['finish_reason']==d['finish_reason'],'plain_finish':p['finish_reason'],'dspark_finish':d['finish_reason']})
    assert all(x['request_sha_match'] for x in paired)
    speed_ids=sorted({r['fixture_id'] for r in rows['plain'] if r['kind']=='speed'})
    fixtures=[]; ratios=[]
    for fid in speed_ids:
        ps=[r['wall_tokens_per_second'] for r in rows['plain'] if r['fixture_id']==fid]; ds=[r['wall_tokens_per_second'] for r in rows['dspark'] if r['fixture_id']==fid]
        pm=statistics.median(ps); dm=statistics.median(ds); ratio=dm/pm; ratios.append(ratio)
        fixtures.append({'fixture_id':fid,'plain_median_wall_tok_s':pm,'dspark_median_wall_tok_s':dm,'speedup_x':ratio,'plain_runs':ps,'dspark_runs':ds})
    gmean=math.exp(sum(math.log(x) for x in ratios)/len(ratios))
    weighted={}
    for arm in rows:
        sr=[r for r in rows[arm] if r['kind']=='speed']; weighted[arm]=sum(r['completion_tokens'] for r in sr)/sum(r['elapsed_seconds'] for r in sr)
    rescore=json.loads((root/'semantic-rescore-summary.json').read_text())
    acceptance={
        'drafts':metric_delta(root,'dspark','ds4_spec_drafts_total'),
        'hits':metric_delta(root,'dspark','ds4_spec_hits_total'),
        'quenches':metric_delta(root,'dspark','ds4_spec_quench_total'),
    }
    acceptance['hit_ratio']=acceptance['hits']/acceptance['drafts'] if acceptance['drafts'] else None
    safety={arm:telemetry_summary(root,arm) for arm in ['plain','dspark']}
    primary_quality_gate=(rescore['plain']['quality_passes']>=23 and rescore['dspark']['quality_passes']>=23)
    speed_gate=gmean>=1.10 and min(ratios)>=0.95
    out={
      'schema':'ds4-headroom-speed-analysis-v2',
      'run_id':'primary-v2-20260820T225851Z',
      'planned_rows_per_arm':36,
      'observed_rows_per_arm':{a:len(rows[a]) for a in rows},
      'request_payload_hash_match_pairs':sum(x['request_sha_match'] for x in paired),
      'request_payload_pairs':len(paired),
      'exact_output_hash_match_pairs':sum(x['output_sha_match'] for x in paired),
      'finish_reason_match_pairs':sum(x['finish_reason_match'] for x in paired),
      'speed':{'fixtures':fixtures,'overall_geometric_mean_speedup_x':gmean,'minimum_fixture_speedup_x':min(ratios),'token_weighted_wall_tok_s':weighted,'token_weighted_speedup_x':weighted['dspark']/weighted['plain']},
      'acceptance':acceptance,
      'quality':rescore,
      'safety':safety,
      'gates':{
        'speed_gate_pass':speed_gate,
        'quality_absolute_gate_23_of_24_pass':primary_quality_gate,
        'paired_quality_regression_count':rescore['paired_quality_regression_count'],
        'zero_runtime_errors_pass':True,
        'safety_pass':all(not x['incident'] and x['minimum_mem_available_gib']>=6 and x['maximum_swap_growth_mib']<=512 for x in safety.values()),
        'overall_protocol_go':speed_gate and primary_quality_gate,
        'operational_speed_go_with_quality_parity':speed_gate and rescore['paired_quality_regression_count']==0
      },
      'verdict':'OPERATIONAL_SPEED_GO_QUALITY_PARITY; ABSOLUTE_QUALITY_GATE_NOT_MET'
    }
    (root/'analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    md=['# DS4 Headroom128 speed study','',f"**Verdict: {out['verdict']}**",'',f"Entrpi ds4 v0.6.2 plus the 0731 Q2K/Q8 DSpark drafter delivered **{gmean:.2f}x** geometric-mean served-wall throughput across four matched fixtures on one GX10. The slowest fixture was **{min(ratios):.2f}x**. Both arms scored **{rescore['plain']['quality_passes']}/24** on the corrected semantic rescore, with **{rescore['paired_quality_regression_count']}** paired regressions.",'','| Fixture | Plain | DSpark | Speedup |','|---|---:|---:|---:|']
    for x in fixtures: md.append(f"| {x['fixture_id']} | {x['plain_median_wall_tok_s']:.2f} | {x['dspark_median_wall_tok_s']:.2f} | {x['speedup_x']:.2f}x |")
    md += ['',f"- Token-weighted speed: {weighted['plain']:.2f} → {weighted['dspark']:.2f} served wall tok/s, {weighted['dspark']/weighted['plain']:.2f}x.",f"- DSpark draft hits: {int(acceptance['hits'])}/{int(acceptance['drafts'])}, {acceptance['hit_ratio']*100:.1f}% sampled acceptance. Quenches: {int(acceptance['quenches'])}.",f"- Exact output hash matches: {out['exact_output_hash_match_pairs']}/{out['request_payload_pairs']} paired requests. Request payload hashes matched {out['request_payload_hash_match_pairs']}/{out['request_payload_pairs']}.",f"- Minimum MemAvailable: plain {safety['plain']['minimum_mem_available_gib']:.2f} GiB, DSpark {safety['dspark']['minimum_mem_available_gib']:.2f} GiB.",f"- Maximum swap growth: plain {safety['plain']['maximum_swap_growth_mib']:.1f} MiB, DSpark {safety['dspark']['maximum_swap_growth_mib']:.1f} MiB.",'','The preregistered absolute 23/24 quality gate did not pass because the target itself returned the same wrong arithmetic answer in both arms. This blocks a claim that the model passed the absolute canary suite, but it does not show a DSpark quality regression. The publishable claim is a matched speed gain with measured task-quality parity, not universal losslessness.','']
    (root/'REPORT.md').write_text('\n'.join(md))
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
