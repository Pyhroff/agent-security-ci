#!/usr/bin/env python3
"""Run adversarial/benign challenge fixtures without changing the CI gate contract."""
from __future__ import annotations
import json, subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "benchmark" / "challenge.json"

CASES = [
    ("mcpaudit", "rephrased_attack", False, ["mcpaudit","scan","--fail-on","high","--","python","toy_agent/challenge/mcp_server_rephrased.py"]),
    ("mcpaudit", "benign_security_doc", True, ["mcpaudit","scan","--fail-on","high","--","python","toy_agent/challenge/mcp_benign_security_doc.py"]),
    ("loopcheck", "rephrased_loop", False, ["loopcheck","analyze","toy_agent/challenge/loop_trace_rephrased.json","--fail-on","medium"]),
    ("loopcheck", "benign_refresh", True, ["loopcheck","analyze","toy_agent/challenge/loop_benign_refresh.json","--fail-on","medium"]),
    ("memsentry", "rephrased_attack", False, ["memsentry","toy_agent/challenge/memory_rephrased.md","--fail-on","high"]),
    ("memsentry", "benign_security_doc", True, ["memsentry","toy_agent/challenge/memory_benign_security.md","--fail-on","high"]),
    ("ragsentry", "rephrased_attack", False, ["ragsentry","toy_agent/challenge/rag_rephrased.md","--fail-on","high"]),
    ("ragsentry", "benign_security_doc", True, ["ragsentry","toy_agent/challenge/rag_benign_security.md","--fail-on","high"]),
    ("trainsentry", "rephrased_attack", False, ["trainsentry","toy_agent/challenge/training_rephrased.jsonl","--fail-on","high"]),
    ("trainsentry", "benign_security_doc", True, ["trainsentry","toy_agent/challenge/training_benign_security.jsonl","--fail-on","high"]),
]

def run(cmd):
    try:
        p=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,check=False)
        return p.returncode,p.stdout[-3000:]
    except OSError as exc:
        return 127,f"{type(exc).__name__}: {exc}"

def metrics(rows):
    tp=sum((not r["expected_pass"]) and r["exit_code"]!=0 for r in rows)
    fn=sum((not r["expected_pass"]) and r["exit_code"]==0 for r in rows)
    tn=sum(r["expected_pass"] and r["exit_code"]==0 for r in rows)
    fp=sum(r["expected_pass"] and r["exit_code"]!=0 for r in rows)
    precision=tp/(tp+fp) if tp+fp else 1.0
    recall=tp/(tp+fn) if tp+fn else 1.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"cases":len(rows),"tp":tp,"fp":fp,"tn":tn,"fn":fn,
            "precision":precision,"recall":recall,"f1":f1,
            "false_positive_rate":fp/(fp+tn) if fp+tn else 0.0,
            "challenge_contract_pass":all(r["contract_pass"] for r in rows)}

def main():
    rows=[]
    for scanner,case,should_pass,cmd in CASES:
        code,out=run(cmd)
        rows.append({"scanner":scanner,"case":case,"expected_pass":should_pass,
                     "exit_code":code,"contract_pass":(code==0)==should_pass,
                     "output_tail":out})
    by=defaultdict(list)
    for row in rows: by[row["scanner"]].append(row)
    report={"benchmark":"agent-security-ci adversarial challenge corpus",
            "scope":"rephrased attacks and benign security-context controls; non-gating",
            "cases":rows,"confusion_matrix":{k:metrics(rows)[k] for k in ("tp","fp","tn","fn")},
            "metrics":{k:metrics(rows)[k] for k in ("precision","recall","f1","false_positive_rate")},
            "by_scanner":{s:metrics(v) for s,v in sorted(by.items())}}
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    # Deliberately never fails the security gate: challenge results are evidence,
    # not a release contract. Any mismatch is surfaced in the summary/artifact.
    return 0

if __name__=="__main__":
    raise SystemExit(main())
