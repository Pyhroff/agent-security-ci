#!/usr/bin/env python3
"""Run the controlled scanner regression corpus and emit machine-readable metrics."""
from __future__ import annotations
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'benchmark' / 'latest.json'

CASES = [
    ('mcpaudit','clean_mcp',True,['mcpaudit','scan','--fail-on','high','--','python','toy_agent/clean/mcp_server.py']),
    ('mcpaudit','vulnerable_mcp',False,['mcpaudit','scan','--fail-on','high','--','python','toy_agent/vulnerable/mcp_server.py']),
    ('loopcheck','clean_trace',True,['loopcheck','analyze','toy_agent/clean/trace.json','--fail-on','medium']),
    ('loopcheck','vulnerable_trace',False,['loopcheck','analyze','toy_agent/vulnerable/trace.json','--fail-on','medium']),
    ('memsentry','clean_memory',True,['memsentry','toy_agent/clean/memory.md','--fail-on','high']),
    ('memsentry','vulnerable_memory',False,['memsentry','toy_agent/vulnerable/memory.md','--fail-on','high']),
    ('ragsentry','clean_rag',True,['ragsentry','toy_agent/clean/rag_doc.md','--fail-on','high']),
    ('ragsentry','vulnerable_rag',False,['ragsentry','toy_agent/vulnerable/rag_doc.md','--fail-on','high']),
    ('trainsentry','clean_training',True,['trainsentry','toy_agent/clean/training_data.jsonl','--fail-on','high']),
    ('trainsentry','vulnerable_training',False,['trainsentry','toy_agent/vulnerable/training_data.jsonl','--fail-on','high']),
]

def run(cmd):
    p = subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    return p.returncode,p.stdout[-4000:]

def main():
    rows=[]
    for scanner,case,should_pass,cmd in CASES:
        code,output=run(cmd)
        passed=(code==0)==should_pass
        rows.append({'scanner':scanner,'case':case,'expected_pass':should_pass,'exit_code':code,'contract_pass':passed,'output_tail':output})
    tp=sum((not r['expected_pass']) and r['exit_code']!=0 for r in rows)
    fn=sum((not r['expected_pass']) and r['exit_code']==0 for r in rows)
    tn=sum(r['expected_pass'] and r['exit_code']==0 for r in rows)
    fp=sum(r['expected_pass'] and r['exit_code']!=0 for r in rows)
    precision=tp/(tp+fp) if tp+fp else 1.0
    recall=tp/(tp+fn) if tp+fn else 1.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    report={'benchmark':'agent-security-ci controlled regression corpus','scope':'checked-in fixtures only; not a production detection claim','cases':rows,'confusion_matrix':{'tp':tp,'fp':fp,'tn':tn,'fn':fn},'metrics':{'precision':precision,'recall':recall,'f1':f1,'false_positive_rate':fp/(fp+tn) if fp+tn else 0.0},'contract_pass':all(r['contract_pass'] for r in rows)}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['contract_pass'] else 1)

if __name__=='__main__': main()