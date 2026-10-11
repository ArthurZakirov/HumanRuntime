#!/usr/bin/env python3
"""Prepare REWE basket quantities using known product IDs, without checkout.

Use a complete, separate manifest for exactly ONE future delivery:
  {"items":[{"id":"7144527","quantity":1},
            {"id":"8245760","quantity":6}]}

IDs (and required variant parameters) are resolved against the locally
exported account product catalogue. No fuzzy matching or unreviewed SKU swaps.
Dry-run by default. --apply only changes basket quantities; it never checks
out, submits, pays, or changes the delivery appointment.

WARNING: REWE basket is account-wide, not per browser tab or delivery date.
Only run --apply when the current account basket belongs to the intended order.
"""
import argparse
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlencode, urlparse, parse_qs


CATALOG = Path.home() / ".local/share/humanruntime/rewe-products.json"


@dataclass(frozen=True)
class Target:
    product_id: str
    variant_id: str | None
    title: str
    quantity: int
    max_price: Decimal | None

    @property
    def url(self) -> str:
        root = f"https://www.rewe.de/shop/products/{self.product_id}"
        return root + ("?" + urlencode({"variantArticleId": self.variant_id}) if self.variant_id else "")


def prepare_targets(manifest: dict, catalogue: dict) -> list[Target]:
    """Validate all requests against the exact items previously seen on REWE."""
    if not isinstance(manifest, dict) or not isinstance(manifest.get("items"), list) or not manifest["items"]:
        raise ValueError("Manifest must contain a nonempty items list")
    products = catalogue.get("favorites", []) + catalogue.get("purchased", [])
    if len(catalogue.get("favorites", [])) != catalogue.get("favorites_expected") or len(catalogue.get("purchased", [])) != catalogue.get("purchased_expected"):
        raise ValueError("The REWE catalogue export was incomplete: refresh before use")

    by_id: dict[str, list[dict]] = {}
    for item in products:
        if isinstance(item.get("id"), str):
            by_id.setdefault(item["id"], []).append(item)
    seen = set()
    targets = []
    for line in manifest["items"]:
        if not isinstance(line, dict):
            raise ValueError("Each item must be a JSON object")
        product_id = line.get("id")
        quantity = line.get("quantity")
        variant = line.get("variant_id")
        if not isinstance(product_id, str) or not re.fullmatch(r"[0-9]{2,12}", product_id):
            raise ValueError(f"Invalid REWE product ID: {product_id!r}")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or not 1 <= quantity <= 300:
            raise ValueError(f"{product_id}: quantity must be a whole number from 1 to 300")
        if variant is not None and (not isinstance(variant, str) or not re.fullmatch(r"[a-zA-Z0-9_-]{2,32}", variant)):
            raise ValueError(f"{product_id}: invalid variant ID")
        listings = by_id.get(product_id, [])
        if variant is not None:
            listings = [p for p in listings if p.get("variant_id") == variant]
        variants = {(p.get("variant_id"), p["title"]) for p in listings}
        if len(variants) != 1:
            raise ValueError(f"{product_id}: product missing or ambiguous in catalogue; variants={sorted(map(str,variants))}")
        variant_id, title = next(iter(variants))
        if "title" in line and line["title"] != title:
            raise ValueError(f"{product_id}: expected title does not match catalogue: {title}")
        key = (product_id, variant_id)
        if key in seen:
            raise ValueError(f"{product_id}: repeated item")
        seen.add(key)

        max_price = None
        if "max_unit_price_eur" in line:
            try:
                max_price = Decimal(str(line["max_unit_price_eur"]))
            except (InvalidOperation, TypeError) as e:
                raise ValueError(f"{product_id}: invalid price cap") from e
            if not max_price.is_finite() or max_price <= 0:
                raise ValueError(f"{product_id}: invalid price cap")
        targets.append(Target(product_id, variant_id, title, quantity, max_price))
    return targets


def browser(*args: str) -> str:
    process = subprocess.run(["agent-browser", *args], capture_output=True, text=True, timeout=45)
    if process.returncode:
        raise RuntimeError(f"agent-browser {args[0]} failed: {(process.stderr or process.stdout)[:400]}")
    return process.stdout.strip()


READ_PRODUCT = r"""(() => {
    const name=document.querySelector('h1')?.textContent?.trim() || null;
    const input=document.querySelector('input[aria-label="Bestellmenge"]');
    const buttons=[...document.querySelectorAll('button')];
    const add=buttons.find(b=>b.getAttribute('aria-label')==='Produkt hinzufügen');
    const qty=input ? Number(input.value) : add ? 0 : null;
    const entireText=document.body.innerText;
    const priceBlock=document.querySelector('.pdpr-Price__Price.rs-qa-price');
    return { url:location.href, title:name, quantity:qty,
        can_add:!!add && add.getAttribute('aria-disabled')!=='true',
        price_text:priceBlock?.textContent || null,
        signed_in:entireText.includes('Arthur') || !!document.querySelector('button[aria-label="Arthur"]'),
        cart_label:buttons.find(b=>/Warenkorb mit/.test(b.getAttribute('aria-label')||''))?.getAttribute('aria-label') || null
    };
})()"""


def read_product() -> dict:
    return json.loads(browser("eval", READ_PRODUCT))


def open_product(target: Target) -> dict:
    browser("open", target.url)
    for i in range(12):
        state = read_product()
        if state["title"] is not None and state["quantity"] is not None:
            return state
        time.sleep(0.3)
    raise RuntimeError(f"{target.product_id}: product page inaccessible or item unavailable")


def assert_same_product(target: Target, state: dict) -> None:
    path = urlparse(state["url"]).path
    if not (path.startswith("/shop/products/") or path.startswith("/shop/p/")) or not path.endswith("/" + target.product_id):
        raise RuntimeError(f"{target.product_id}: unexpected page {state['url']!r}")
    redirect_variant = parse_qs(urlparse(state["url"]).query).get("variantArticleId", [None])[0]
    if target.variant_id and redirect_variant and redirect_variant != target.variant_id:
        raise RuntimeError(f"{target.product_id}: variant changed: {redirect_variant}")
    norm = lambda text: " ".join(text.casefold().split())
    if norm(state["title"]) != norm(target.title):
        raise RuntimeError(f"{target.product_id}: title changed: {state['title']!r}")


def german_price(value: str | None) -> Decimal | None:
    if not value:
        return None
    match = re.search(r"(\d+(?:\.\d{3})*,\d{2})\s*€", value)
    if not match:
        return None
    return Decimal(match.group(1).replace(".", "").replace(",", "."))


def run(target: Target, apply: bool) -> dict:
    state = open_product(target)
    assert_same_product(target, state)
    price = german_price(state["price_text"])
    if target.max_price is not None and (price is None or price > target.max_price):
        raise RuntimeError(f"{target.product_id}: live price {price} exceeds or cannot verify ceiling {target.max_price}")
    before = state["quantity"]
    result = {"id":target.product_id, "variant_id":target.variant_id, "title":target.title,
              "before":before, "target":target.quantity,
              "live_unit_price_eur":str(price) if price is not None else None,
              "status":"already_correct" if before == target.quantity else "would_set"}
    if before == target.quantity or not apply:
        return result
    if before == 0:
        if not state["can_add"]:
            raise RuntimeError(f"{target.product_id}: unavailable; not adding substitute")
        browser("find", "role", "button", "click", "--name", "Produkt hinzufügen")
        time.sleep(.3)
    browser("fill", 'input[aria-label="Bestellmenge"]', str(target.quantity))
    browser("press", "Tab")
    for _ in range(12):
        time.sleep(.3)
        verified = read_product()
        if verified["quantity"] == target.quantity:
            assert_same_product(target, verified)
            result["status"] = "set"
            return result
    raise RuntimeError(f"{target.product_id}: failed quantity confirmation; expected {target.quantity}, observed {verified['quantity']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tab", required=True, help="A REWE browser tab, e.g. t8")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--catalogue", default=CATALOG, type=Path)
    parser.add_argument("--apply", action="store_true", help="Change basket; no checkout")
    parser.add_argument("--report", type=Path)
    args=parser.parse_args()
    manifest=json.loads(args.manifest.read_text())
    catalogue=json.loads(args.catalogue.read_text())
    targets=prepare_targets(manifest, catalogue)
    browser("tab", args.tab)
    tab_url = browser("get", "url")
    if not tab_url.startswith("https://www.rewe.de/shop/"):
        raise RuntimeError("The selected tab is not the REWE shop")
    results=[]
    for target in targets:
        try:
            outcome = run(target, apply=args.apply)
        except Exception as exc:
            outcome={"id":target.product_id,"title":target.title,"status":"blocked","reason":str(exc)}
        print(json.dumps(outcome, ensure_ascii=False),flush=True)
        results.append(outcome)
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n")
    if any(x["status"]=="blocked" for x in results):
        raise SystemExit(1)


if __name__=="__main__":
    main()
