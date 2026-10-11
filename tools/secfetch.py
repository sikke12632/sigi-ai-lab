"""Cached, rate-limited fetcher for SEC EDGAR and other public sources.

CLI:
  python3 tools/secfetch.py fetch URL            -> path of cached raw file
  python3 tools/secfetch.py text URL [--grep RE] -> plain text (same extraction the verifier uses)
  python3 tools/secfetch.py filings CIK [--since YYYY-MM-DD] [--forms 8-K,10-Q]
  python3 tools/secfetch.py index CIK ACCESSION  -> documents in a filing
  python3 tools/secfetch.py facts CIK TAG [--unit USD] -> XBRL facts for a tag (companyfacts)

SEC fair-access: identifiable User-Agent (override with SEC_USER_AGENT) and a
global rate limit shared by every process on this machine (<= ~6 req/s).
"""
import argparse
import fcntl
import gzip
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".cache")
SEC_UA = os.environ.get("SEC_USER_AGENT", "SigiAiLab-PersonalResearch research-contact@example.com")
WEB_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
MIN_INTERVAL = 0.17


def _throttle():
    os.makedirs(CACHE, exist_ok=True)
    with open(os.path.join(CACHE, ".ratelimit"), "a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.seek(0)
        try:
            last = float(f.read().strip() or 0)
        except ValueError:
            last = 0.0
        wait = last + MIN_INTERVAL - time.time()
        if wait > 0:
            time.sleep(wait)
        f.seek(0)
        f.truncate()
        f.write(str(time.time()))
        fcntl.flock(f, fcntl.LOCK_UN)


def cache_path(url):
    return os.path.join(CACHE, hashlib.sha256(url.encode()).hexdigest()[:32])


def fetch(url, refresh=False):
    """Return raw bytes for url, from cache when available."""
    path = cache_path(url)
    if os.path.exists(path) and not refresh:
        with open(path, "rb") as f:
            return f.read()
    is_sec = "sec.gov" in url
    headers = {"User-Agent": SEC_UA if is_sec else WEB_UA, "Accept-Encoding": "gzip"}
    last_err = None
    for attempt in range(4):
        if is_sec:
            _throttle()
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
            os.makedirs(CACHE, exist_ok=True)
            with open(path, "wb") as f:
                f.write(data)
            return data
        except Exception as e:  # retry transient errors
            last_err = e
            code = getattr(e, "code", None)
            if code in (403, 404) and attempt >= 1:
                break
            time.sleep(2 ** attempt)
    raise RuntimeError(f"fetch failed {url}: {last_err}")


class _Text(HTMLParser):
    BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "article"}
    CELL = {"td", "th"}
    SKIP = {"script", "style", "ix:header", "head", "noscript"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.out.append("\n")
        elif tag in self.CELL:
            self.out.append(" ")

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in self.BLOCK:
            self.out.append("\n")
        elif tag in self.CELL:
            self.out.append(" ")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def to_text(data, url=""):
    if data[:5] == b"%PDF-" or url.lower().endswith(".pdf"):
        p = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True)
        txt = p.stdout.decode("utf-8", "replace")
    else:
        raw = data.decode("utf-8", "replace")
        if "<" in raw[:2000] or "<html" in raw.lower()[:5000]:
            parser = _Text()
            parser.feed(raw)
            txt = "".join(parser.out)
        else:
            txt = raw
    txt = html.unescape(txt).replace("\xa0", " ").replace("​", "")
    txt = re.sub(r"[ \t\r\f\v]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return txt.strip()


def text(url):
    return to_text(fetch(url), url)


def norm(s):
    """Normalisation used when checking that a quote appears in a source."""
    s = html.unescape(s).replace("\xa0", " ").replace("​", "")
    for a, b in (("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("−", "-"), ("•", "*")):
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def quote_in(quote, source_text):
    """'exact' if found after whitespace/typography normalisation, 'nospace' if found
    only once all whitespace is dropped (table-cell splits), else None."""
    q, t = norm(quote), norm(source_text)
    if q and q in t:
        return "exact"
    q2, t2 = re.sub(r"\s", "", q), re.sub(r"\s", "", t)
    if q2 and q2 in t2:
        return "nospace"
    return None


def cik10(cik):
    return str(int(cik)).zfill(10)


def submissions(cik):
    d = json.loads(fetch(f"https://data.sec.gov/submissions/CIK{cik10(cik)}.json", refresh=True))
    rows = []
    blocks = [d["filings"]["recent"]] + [
        json.loads(fetch("https://data.sec.gov/submissions/" + f["name"])) for f in d["filings"].get("files", [])
    ]
    for r in blocks:
        for i in range(len(r["accessionNumber"])):
            rows.append({k: r[k][i] for k in ("accessionNumber", "form", "filingDate", "reportDate",
                                               "primaryDocument", "items", "acceptanceDateTime")})
    return d, rows


def filing_url(cik, accession, doc=""):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{doc}"


def filing_index(cik, accession):
    d = json.loads(fetch(filing_url(cik, accession, "index.json")))
    return [(i["name"], i.get("type", ""), i.get("size", "")) for i in d["directory"]["item"]]


def companyfacts(cik):
    return json.loads(fetch(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10(cik)}.json", refresh=False))


def facts(cik, tag, unit="USD"):
    cf = companyfacts(cik)
    ns, _, name = tag.partition(":") if ":" in tag else ("us-gaap", "", tag)
    ns = {"us-gaap": "us-gaap", "dei": "dei"}.get(ns, ns)
    try:
        return cf["facts"][ns][name]["units"][unit]
    except KeyError:
        return []


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("fetch"); a.add_argument("url"); a.add_argument("--refresh", action="store_true")
    a = sub.add_parser("text"); a.add_argument("url"); a.add_argument("--grep"); a.add_argument("-C", type=int, default=300)
    a = sub.add_parser("filings"); a.add_argument("cik"); a.add_argument("--since", default=""); a.add_argument("--forms", default="")
    a = sub.add_parser("index"); a.add_argument("cik"); a.add_argument("accession")
    a = sub.add_parser("facts"); a.add_argument("cik"); a.add_argument("tag"); a.add_argument("--unit", default="USD"); a.add_argument("--since", default="")
    args = ap.parse_args()

    if args.cmd == "fetch":
        fetch(args.url, args.refresh)
        print(cache_path(args.url))
    elif args.cmd == "text":
        t = text(args.url)
        if args.grep:
            for m in re.finditer(args.grep, t, flags=re.I):
                s, e = max(0, m.start() - args.C), min(len(t), m.end() + args.C)
                print("…" + t[s:e].replace("\n", " ⏎ ") + "…\n---")
        else:
            print(t)
    elif args.cmd == "filings":
        d, rows = submissions(args.cik)
        forms = set(args.forms.split(",")) if args.forms else None
        print(d["name"], d.get("fiscalYearEnd"))
        for r in rows:
            if r["filingDate"] >= args.since and (not forms or r["form"] in forms):
                print(r["filingDate"], r["form"], r["accessionNumber"], r["reportDate"], r["items"],
                      filing_url(args.cik, r["accessionNumber"], r["primaryDocument"]))
    elif args.cmd == "index":
        for name, typ, size in filing_index(args.cik, args.accession):
            print(name, typ, size, filing_url(args.cik, args.accession, name))
    elif args.cmd == "facts":
        for f in facts(args.cik, args.tag, args.unit):
            if f.get("filed", "") >= args.since:
                print(json.dumps(f))


if __name__ == "__main__":
    sys.exit(main())
