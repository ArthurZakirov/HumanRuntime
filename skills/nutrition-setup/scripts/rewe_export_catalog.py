#!/usr/bin/env python3
"""Export every REWE favorite and purchased product ID from the logged-in browser.

Saves locally by default (NOT in Git). Read-only: never changes cart or favorites.
The expected item counts must match actual unique product rows; a partial lazy
load must not be accepted as complete.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import parse_qs, urlparse

DEFAULT_OUTPUT = Path.home() / ".local/share/humanruntime/rewe-products.json"

EXTRACT = r"""(() => ({
    expected: Number(document.body.innerText.match(/Alle Kategorien\s*\((\d+)\)/)?.[1] || 0),
    products: [...document.querySelectorAll('.lrms-tileContent')].map(c => ({
      title: c.querySelector('h2 a')?.getAttribute('title') ||
             c.querySelector('h2 a')?.textContent.trim(),
      href: c.querySelector('h2 a')?.getAttribute('href'),
      price_text: c.querySelector('.lrms-productTilePriceWrapper')?.textContent.trim() || null,
      unavailable: c.innerText.includes('Nicht verfügbar')
    })).filter(x => x.href && x.title)
}))()"""


def browser(*args: str) -> str:
    p=subprocess.run(["agent-browser", *args],capture_output=True,text=True,timeout=45)
    if p.returncode:
        raise RuntimeError(f"agent-browser failed: {(p.stderr or p.stdout)[:400]}")
    return p.stdout.strip()


def parse_listings(items: list[dict], category: str) -> list[dict]:
    result=[]
    for item in items:
        match = re.fullmatch(r"/shop/products/(\d+)(?:\?.*)?", item["href"])
        if not match:
            raise ValueError(f"Unexpected product URL: {item['href']!r}")
        product_id=match.group(1)
        variant_id=parse_qs(urlparse(item["href"]).query).get("variantArticleId",[None])[0]
        result.append({**item, "id":product_id, "variant_id":variant_id,
                       "url":"https://www.rewe.de"+item["href"],
                       "source":category})
    return result


def export_page(tab: str, category: str) -> tuple[list[dict],int]:
    browser("tab",tab)
    browser("open","https://www.rewe.de/shop/deine-produkte?favList="+("true" if category=="favorites" else "false"))
    data={"expected":0,"products":[]}
    listings={}
    for i in range(20):
        time.sleep(.2)
        data=json.loads(browser("eval",EXTRACT))
        for p in parse_listings(data["products"],category):
            listings[(p["id"],p["variant_id"])]=p
        expected=data["expected"]
        if expected and len(listings)>=expected:
            break
        browser("scroll","down","4400")
    if not expected or len(listings)!=expected:
        raise RuntimeError(f"{category}: incomplete product collection ({len(listings)}/{expected}), refusing export")
    print(f"{category}: {len(listings)}/{expected} unique listings",flush=True)
    return list(listings.values()),expected


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tab",required=True)
    ap.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    args=ap.parse_args()
    favorites,fc=export_page(args.tab,"favorites")
    purchased,pc=export_page(args.tab,"purchased")
    payload={"source":"REWE logged-in favorites/purchased browser UI",
             "favorites_expected":fc,"purchased_expected":pc,
             "favorites":favorites,"purchased":purchased}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n")
    os.chmod(args.output,0o600)
    print(f"Saved {args.output}; {len({x['id'] for x in favorites+purchased})} unique product IDs",flush=True)


if __name__=="__main__":
    main()
