"""Validate gold_cloud/{TICKER}.json files.

Checks: schema shape and enums, cutoff dates, choi xbrl.value == value_usd and the
value against SEC companyfacts, and that every quote (choi + kim) appears in its
source document (re-fetched; cached raw bytes are reused).

  python3 tools/verify_gold.py gold_cloud/CMS.json [...]
"""
import json
import re
import sys

sys.path.insert(0, __import__("os").path.dirname(__file__))
import secfetch as sf  # noqa: E402

CUTOFF = "2026-10-11"
WINDOW_START = "2026-04-14"
CHOI_TARGETS = ["operating_income", "short_term_borrowings", "current_long_term_debt_ex_leases", "current_finance_leases"]
STATUSES = {"value", "none_presented", "not_determinable"}
SECTIONS = {"1_results", "2_cash_debt", "3_guidance", "4_events", "5_legal", "6_risks", "7_industry"}
TIERS = {"required", "optional", "background"}
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def doc_url(cik, doc, latest):
    """Resolve a choi source.doc ('10-Q 0000000000-26-000000[ / file.htm]') to a URL."""
    m = re.search(r"(\d{10}-\d{2}-\d{6})", doc or "")
    if not m:
        return None
    acc = m.group(1)
    fm = re.search(r"([\w\-.]+\.html?)", doc)
    if fm:
        return sf.filing_url(cik, acc, fm.group(1))
    _, rows = sf.submissions(cik)
    for r in rows:
        if r["accessionNumber"] == acc:
            return sf.filing_url(cik, acc, r["primaryDocument"])
    return None


def check(path):
    errs, warns = [], []
    g = json.load(open(path))
    for k in ("company", "cutoff", "latest_periodic_report", "choi", "kim", "searched_not_found"):
        if k not in g:
            errs.append(f"missing top-level key {k}")
    if errs:
        return errs, warns
    cik = g["company"]["cik"]
    lpr = g["latest_periodic_report"]
    if g["cutoff"] != CUTOFF:
        errs.append("cutoff mismatch")
    if lpr.get("filed", "9") > CUTOFF:
        errs.append("latest periodic report filed after cutoff")
    _, rows = sf.submissions(cik)
    accs = {r["accessionNumber"]: r for r in rows}
    r = accs.get(lpr.get("accession"))
    if not r:
        errs.append(f"latest_periodic_report accession not found {lpr.get('accession')}")
    else:
        if r["form"] != lpr["form"] or r["filingDate"] != lpr["filed"] or r["reportDate"] != lpr["period_end"]:
            errs.append(f"latest_periodic_report mismatch with EDGAR: {r['form']} {r['filingDate']} {r['reportDate']}")
        later = [x for x in rows if x["form"] in ("10-Q", "10-K", "10-Q/A", "10-K/A", "10-KT")
                 and lpr["filed"] < x["filingDate"] <= CUTOFF]
        if later:
            errs.append(f"a later periodic report exists: {later[0]['form']} {later[0]['filingDate']}")

    # choi
    targets = [c.get("target") for c in g["choi"]]
    if sorted(targets) != sorted(CHOI_TARGETS):
        errs.append(f"choi targets {targets}")
    main_url = doc_url(cik, lpr.get("accession", ""), lpr)
    for c in g["choi"]:
        t = c.get("target")
        if c.get("status") not in STATUSES:
            errs.append(f"choi {t}: bad status")
        if c.get("status") == "value":
            x = c.get("xbrl")
            if x and x.get("value") is not None and x["value"] != c.get("value_usd") and not c.get("note"):
                errs.append(f"choi {t}: xbrl.value != value_usd and no note")
            if x and x.get("tag"):
                fs = sf.facts(cik, x["tag"])
                hit = [f for f in fs if f.get("accn") == lpr.get("accession") and f.get("end") == c.get("period_end")
                       and f.get("start", c.get("period_start")) == c.get("period_start")]
                if not hit:
                    warns.append(f"choi {t}: no companyfacts fact for {x['tag']} in {lpr.get('accession')} ending {c.get('period_end')}")
                elif not any(f["val"] == x.get("value") for f in hit):
                    errs.append(f"choi {t}: companyfacts {x['tag']} = {[f['val'] for f in hit]} vs xbrl.value {x.get('value')}")
        src = c.get("source") or {}
        q = src.get("quote")
        if q:
            url = doc_url(cik, src.get("doc", ""), lpr) or main_url
            try:
                how = sf.quote_in(q, sf.text(url))
            except Exception as e:
                how = None
                warns.append(f"choi {t}: could not fetch {url}: {e}")
            if not how:
                errs.append(f"choi {t}: quote not found in {url}: {q[:80]!r}")
        elif c.get("status") != "not_determinable":
            errs.append(f"choi {t}: no quote")

    # kim
    ids = set()
    for k in g["kim"]:
        i = k.get("id")
        if i in ids:
            errs.append(f"duplicate id {i}")
        ids.add(i)
        if k.get("section") not in SECTIONS:
            errs.append(f"{i}: bad section")
        if k.get("tier") not in TIERS:
            errs.append(f"{i}: bad tier")
        for dk in ("event_date", "published_date"):
            v = k.get(dk)
            if v is not None and not DATE.match(v):
                errs.append(f"{i}: bad {dk} {v}")
        if (k.get("published_date") or "0") > CUTOFF:
            errs.append(f"{i}: published after cutoff")
        ev = k.get("event_date") or k.get("published_date") or ""
        if k.get("tier") != "background" and ev and ev < WINDOW_START and k.get("section") in ("4_events",):
            warns.append(f"{i}: 4_events dated {ev} before window but tier {k.get('tier')}")
        src = k.get("source") or {}
        q, url = src.get("quote", ""), src.get("url", "")
        if not q or not url:
            errs.append(f"{i}: missing quote/url")
            continue
        if len(q) > 300:
            errs.append(f"{i}: quote longer than 300 chars ({len(q)})")
        try:
            how = sf.quote_in(q, sf.text(url))
        except Exception as e:
            errs.append(f"{i}: could not fetch {url}: {e}")
            continue
        if not how:
            errs.append(f"{i}: quote not found in {url}: {q[:80]!r}")
        elif how == "nospace":
            warns.append(f"{i}: quote matched only ignoring whitespace")
    return errs, warns


def main():
    bad = 0
    for p in sys.argv[1:]:
        errs, warns = check(p)
        g = json.load(open(p))
        print(f"== {p}: choi={len(g.get('choi', []))} kim={len(g.get('kim', []))} errors={len(errs)} warnings={len(warns)}")
        for e in errs:
            print("  ERROR", e)
        for w in warns:
            print("  warn ", w)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
