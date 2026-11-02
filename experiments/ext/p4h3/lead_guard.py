"""Guard for the single P4-H3 run: verify every frozen file hash, the sealed bank manifest hash,
and that no P4-H3 output exists (pre) or exactly the expected ones exist (post).
Usage: python experiments/ext/p4h3/lead_guard.py --phase pre|post
Docs that receive appended results (p4h3_rq41/rq44) are hashed in spec_files.json BEFORE appending;
results are therefore recorded only in docs/decision_rules.md, and these docs must stay unchanged.
rq43's doc is hashed over its first doc_prefix.bytes bytes by design."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
RQS = ("rq41", "rq43", "rq44")
BANK_SHA = "af927e3a62e1d0d44d0aebe23fa2867e11643fe389bfe81590710e8d836ea32e"
OUT = {"rq41": ["ext_p4h3_rq41_main", "ext_p4h3_rq41_analysis"], "rq43": ["ext_p4h3_rq43"], "rq44": ["ext_p4h3_rq44_dev", "ext_p4h3_rq44_conf", "ext_p4h3_rq44"]}
def sha(p, n=None):
    b = (ROOT / p).read_bytes()
    return hashlib.sha256(b[:n] if n else b).hexdigest()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", required=True, choices=["pre", "post"]); a = ap.parse_args()
    bad = []
    for rq in RQS:
        sp = json.loads((ROOT / f"experiments/ext/p4h3/{rq}/spec_files.json").read_text())
        for path, h in sp["files"].items():
            h = h["sha256"] if isinstance(h, dict) else h
            n = sp["doc_prefix"]["bytes"] if (rq == "rq43" and path == sp["doc"]) else None
            if sha(path, n) != h: bad.append(f"{rq}: hash mismatch {path}")
    if sha("data/topology_bank/P4-H3/p4h3_manifest.json") != BANK_SHA: bad.append("P4-H3 manifest hash mismatch")
    mans = []
    for m in (ROOT / "results").glob("*/manifest.json"):
        try:
            d = json.loads(m.read_text())
            c = d.get("config", d) if isinstance(d, dict) else {}
            c = c if isinstance(c, dict) else {}
            c = c if "bank" in c else d
        except Exception:
            continue
        if isinstance(c, dict) and c.get("bank") == "P4-H3": mans.append(m.parent.name)
    outs = [d for rq in RQS for d in OUT[rq] if (ROOT / "results" / d).exists()]
    if a.phase == "pre":
        if mans: bad.append(f"P4-H3 manifests exist: {mans}")
        if outs: bad.append(f"outputs exist: {outs}")
    else:
        if sorted(mans) != sorted(["ext_p4h3_rq41_main", "ext_p4h3_rq44_dev", "ext_p4h3_rq44_conf"]) and sorted(mans) != sorted(["ext_p4h3_rq41_main", "ext_p4h3_rq43", "ext_p4h3_rq44_dev", "ext_p4h3_rq44_conf"]):
            bad.append(f"unexpected P4-H3 manifests: {mans}")
    print("\n".join(bad) if bad else f"LEAD GUARD {a.phase.upper()} PASS (manifests with bank P4-H3: {mans})")
    sys.exit(1 if bad else 0)
main()
