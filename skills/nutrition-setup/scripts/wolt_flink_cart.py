#!/usr/bin/env python3
"""Inspect Wolt/Flink search results, then add an EXACT chosen SKU to a cart.

Requires authenticated Chrome tab exposed to agent-browser CLI.
Never checks out or submits an order.

Usage:
  python3 wolt_flink_cart.py --tab t9 --search Paprika --inspect
  python3 wolt_flink_cart.py --tab t9 --search Paprika --exact-title "Paprika Rot 1 Stk." --target 1
"""

import argparse
import json
import re
import subprocess
import sys
import time


SEARCH_SELECTOR = 'input[placeholder="Suche bei Flink Karolinenstraße"]'


def browser(*args: str, timeout: int = 35) -> str:
    p = subprocess.run(["agent-browser", *args], capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"agent-browser {' '.join(args[:2])}: {p.stderr.strip() or p.stdout.strip()}")
    return p.stdout.strip()


def inspect_items():
    script = r"""(() => ({
      query: new URL(location.href).searchParams.get('search'),
      heading_query: document.body.innerText.match(/Suchergebnisse für\s*["“]([^"”]+)["”]/)?.[1] || null,
      loading_query: document.body.innerText.match(/Wir suchen nach\s*["“]([^"”]+)["”]/)?.[1] || null,
      items: [...document.querySelectorAll('li[data-test-id="ItemCard"]')]
        .map(e => ({
          title: e.querySelector('h3[data-test-id="ImageCentricProductCard.Title"]')?.textContent?.trim() || '',
          unit: e.querySelector('[data-test-id="ImageCentricProductCardProductInfo"]')?.textContent?.trim() || '',
          price: e.querySelector('[data-test-id="ImageCentricProductCardPrice"]')?.textContent?.trim() || '',
          quantity: Number(e.querySelector('[data-test-id="ItemCardStepperValue"]')?.textContent?.trim() || 0)
        })).filter(e=>e.title)
    }))()"""
    return json.loads(browser("eval", script))


def cart_counter() -> int | None:
    """Return total current Wolt/Flink cart unit count, if the cart is visible."""
    data = json.loads(browser('eval', """(() => {
      let buttons = [...document.querySelectorAll('button')];
      let b = buttons.find(x => x.textContent?.includes('Bestellung ansehen'));
      return b ? {text: b.textContent.trim()} : null;
    })()"""))
    if not data:
        return None
    match = re.search(r'(\d+)\s*Bestellung ansehen', data['text'])
    return int(match.group(1)) if match else None


def resume_saved_cart() -> bool:
    """Choose 'Ja' only for Wolt's specific 'Bestellung fortsetzen?' dialog.

    On a refreshed closed shop, the background sometimes shows 'Vorbestellung'
    until this dialog is accepted. Never choose 'Nein': it means abandoning the
    saved cart and beginning a new one.
    """
    tree = browser('snapshot', '-i')
    if not re.search(r'^- heading "Bestellung fortsetzen\?"', tree, re.M):
        return False
    match = re.search(r'^- button "Ja" \[ref=(e\d+)\]', tree, re.M)
    if not match:
        raise RuntimeError('Resume-cart dialog seen but Ja button missing; stop to protect saved cart.')
    browser('click', '@' + match.group(1))
    for _ in range(12):
        tree = browser('snapshot', '-i')
        if 'Bestellung fortsetzen?' not in tree and 'Bestellung ansehen' in tree:
            return True
        time.sleep(0.45)
    raise RuntimeError('Clicked Ja but saved basket did not reappear. Stop; do not overwrite the cart.')


def safe_reload() -> None:
    """Recover a frozen Wolt search without discarding the existing cart."""
    before = cart_counter()
    print('SEARCH_STALLED: refreshing the current Wolt tab (cart units before:', before, ')', flush=True)
    browser('reload', timeout=48)
    resumed = False
    for _ in range(15):
        resumed = resume_saved_cart() or resumed
        after = cart_counter()
        if after is not None:
            if before is not None and after != before:
                raise RuntimeError(f'Cart changed across reload: {before} -> {after}; stop before editing.')
            print(f'RELOADED: cart units={after}, resumed_saved_cart={resumed}', flush=True)
            return
        time.sleep(0.5)
    raise RuntimeError('Could not confirm saved Wolt cart after refresh; do not add products.')


def wait_for_search(search: str) -> None:
    """Do not interpret unfinished API responses or previous-query cards as results.

    First allow a short normal search. If Wolt keeps saying 'Wir suchen nach',
    reload this SAME tab, explicitly restore its saved cart with 'Ja', then
    allow another attempt. A timeout is not an out-of-stock verdict.
    """
    for attempt, seconds in enumerate((11, 16)):
        deadline = time.monotonic() + seconds
        previous = None
        stable = 0
        while time.monotonic() < deadline:
            resume_saved_cart()
            state = inspect_items()
            if state['query'] == search and state['heading_query'] == search and state['loading_query'] != search:
                signature = json.dumps(state['items'], ensure_ascii=False)
                if previous == signature:
                    stable += 1
                    if stable >= 2:
                        return
                else:
                    stable = 0
                    previous = signature
            else:
                previous = None
                stable = 0
            time.sleep(0.65)
        if attempt == 0:
            safe_reload()
            now = inspect_items()
            if now['query'] != search:
                browser('fill', SEARCH_SELECTOR, search)
    raise RuntimeError('Wolt search still incomplete after reload. Retry later or use REWE; DO NOT claim unavailable.')


def find_increment_ref(snapshot: str, title: str) -> str:
    lines = snapshot.splitlines()
    title_matches = []
    for i, line in enumerate(lines):
        match = re.match(r'^- heading (".*") \[level=3, ref=e\d+\]$', line)
        if match and json.loads(match.group(1)) == title:
            title_matches.append(i)
    if len(title_matches) != 1:
        raise RuntimeError(f"Expected one product title in snapshot, found {len(title_matches)}: {title!r}")
    i = title_matches[0]
    for line in lines[i + 1:]:
        if line.startswith('- heading ') or (line.startswith('- button ') and ('Preis ' in line or 'Beliebt Preis ' in line)):
            break
        match = re.search(r'- button "Weiteren Artikel hinzufügen" \[ref=(e\d+)\]', line)
        if match:
            return '@' + match.group(1)
    raise RuntimeError(f"No add-plus ref found for {title!r}; inspect snapshot or screenshot.")


def cart_items():
    tree = browser("snapshot", "-i")
    match = re.search(r'- button "[^"]*Bestellung ansehen[^"]*" \[ref=(e\d+)\]', tree)
    if not match:
        raise RuntimeError("Cart button missing; verify manually.")
    browser("click", '@' + match.group(1))
    browser("wait", "--fn", "!!document.querySelector('[data-test-id=CartItem]')", "--timeout", "10000")
    data = json.loads(browser("eval", """(()=>[...document.querySelectorAll('[data-test-id=CartItem]')]
      .map(x=>({
        title:x.querySelector('[data-test-id=CartItemName]')?.textContent?.trim() || '',
        quantity:Number(x.querySelector('[data-test-id=CartItemStepper]')?.value || 0)
      })))()"""))
    # Close only cart dialog, never checkout.
    tree = browser("snapshot", "-i")
    match = re.search(r'- button "Dialogfeld schließen" \[ref=(e\d+)\]', tree)
    if match:
        browser("click", '@' + match.group(1))
    return data



def global_addition_guard(manifest_file: str, wolt_tab: str, rewe_tab: str,
                          exact_title: str, intended_packs: int) -> None:
    """Fail closed BEFORE any plus clicks if another cart owns the same food."""
    from pathlib import Path
    from reconcile_grocery_carts import CartLine, read_rewe, proposed_addition_errors
    data = json.loads(Path(manifest_file).read_text())
    # Cart view is the truth. Search listing count alone cannot verify other shops.
    wolt_rows = [CartLine('wolt', item['title'],item['quantity']) for item in cart_items()]
    try:
        rewe_rows = read_rewe(rewe_tab)
    finally:
        browser('tab', wolt_tab)
    problems=proposed_addition_errors(data,wolt_rows+rewe_rows,'wolt',exact_title,intended_packs)
    if problems:
        raise RuntimeError('GLOBAL CART ALLOCATION BLOCKED: ' + '; '.join(problems))
    print('GLOBAL CART ALLOCATION VERIFIED before write:',exact_title,
          'target packs:',intended_packs,flush=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tab', required=True, help='Existing authenticated Wolt tab, e.g. t9')
    parser.add_argument('--search', help='Search term; omitted only for --recover-only')
    parser.add_argument('--inspect', action='store_true', help='Inspect results and do not add anything')
    parser.add_argument('--recover-only', action='store_true', help='Reload Wolt tab, choose Ja to keep saved cart, then verify unit count; do not add anything')
    parser.add_argument('--exact-title', help='Exact chosen listing name from inspected search results')
    parser.add_argument('--target', type=int, help='Desired total quantity of this exact SKU in the cart')
    parser.add_argument('--manifest', help='REQUIRED on writes: canonical cross-shop goals + SKU mapping JSON')
    parser.add_argument('--rewe-tab', help='REQUIRED on writes: REWE cart tab for global quantity check')
    parser.add_argument('--max-unit-price', type=float, help='Maximum allowed price per listing in EUR')
    args = parser.parse_args()
    if not args.recover_only and not args.search:
        parser.error('--search required unless using --recover-only')
    if not args.inspect and not args.recover_only and (not args.exact_title or args.target is None):
        parser.error('For cart edits provide --exact-title and --target. Use --inspect for research.')
    if not args.inspect and not args.recover_only and not (args.manifest and args.rewe_tab):
        parser.error('Write requires --manifest and --rewe-tab; single-shop target is unsafe.')
    if args.target is not None and not 0 <= args.target <= 30:
        parser.error('--target must be 0 to 30')
    browser('tab', args.tab)
    current_url = browser('get', 'url')
    if 'wolt.com/' not in current_url or '/venue/' not in current_url:
        raise RuntimeError('Current tab is not a Wolt store; refusing to touch another site.')
    if args.recover_only:
        safe_reload()
        return
    resume_saved_cart()
    state = inspect_items()
    # Avoid redundant fill: re-entering a query can leave Wolt loading forever.
    if not (state['query'] == args.search and state['heading_query'] == args.search and
            state['loading_query'] != args.search):
        browser('fill', SEARCH_SELECTOR, args.search)
    wait_for_search(args.search)
    results = inspect_items()
    print(json.dumps(results, ensure_ascii=False, indent=2), flush=True)
    if args.inspect:
        return
    matches = [x for x in results['items'] if x['title'] == args.exact_title]
    if len(matches) != 1:
        raise RuntimeError('Exact product not found; inspect all displayed options or try synonyms. No item added.')
    candidate = matches[0]
    if args.max_unit_price is not None:
        m = re.search(r'(\d+(?:\.\d{3})*,\d{2})', candidate['price'])
        if not m or float(m.group(1).replace('.', '').replace(',', '.')) > args.max_unit_price:
            raise RuntimeError('Price missing or above ceiling; no item added.')
    current = candidate['quantity']
    # Do not write based on a Wolt-only target; eggs may already be in REWE.
    global_addition_guard(args.manifest, args.tab, args.rewe_tab, args.exact_title, args.target)
    if current > args.target:
        raise RuntimeError(f'Already {current} in cart, greater than target {args.target}; do not remove without review.')
    if current == args.target:
        actual = [x for x in cart_items() if x['title'] == args.exact_title]
        if len(actual) != 1 or actual[0]['quantity'] != args.target:
            raise RuntimeError('Product says already in basket, but actual cart does not agree; no edits made.')
        print(f'CONFIRMED existing cart item: {args.exact_title} x {current}', flush=True)
        return
    # Main automation safety boundary: click the card's verified plus, not an
    # unrelated "product info", sponsored card or item with similar keywords.
    snap = browser('snapshot', '-i')
    inc = find_increment_ref(snap, args.exact_title)
    for desired in range(current + 1, args.target + 1):
        browser('click', inc)
        test = json.dumps(args.exact_title, ensure_ascii=False)
        condition = f"""(()=>{{let x=[...document.querySelectorAll('li[data-test-id=ItemCard]')]
          .find(e=>e.querySelector('h3')?.textContent?.trim()==={test});
          return x && Number(x.querySelector('[data-test-id=ItemCardStepperValue]')?.textContent?.trim()||0)>={desired};
        }})()"""
        browser('wait', '--fn', condition, '--timeout', '10000')
    verify = inspect_items()
    now = next((x['quantity'] for x in verify['items'] if x['title']==args.exact_title), -1)
    if now != args.target:
        raise RuntimeError(f'Product-card quantity mismatch: {now} != {args.target}')
    # Second live cross-shop read catches external/cart-state changes during add.
    global_addition_guard(args.manifest, args.tab, args.rewe_tab, args.exact_title, args.target)
    items = cart_items()
    in_cart = [x for x in items if x['title'] == args.exact_title]
    if len(in_cart) != 1 or in_cart[0]['quantity'] != args.target:
        raise RuntimeError(f'Cart verification failed for {args.exact_title}: {in_cart}')
    print(f'CONFIRMED in actual cart: {args.exact_title} x {args.target}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr, flush=True)
        sys.exit(1)
