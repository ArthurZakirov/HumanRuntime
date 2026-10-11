#!/usr/bin/env python3
"""Fail-closed cross-shop grocery cart reconciliation. Read-only; never checks out.

Usage:
    python3 reconcile_grocery_carts.py --manifest /tmp/grocery-plan.json \
        --wolt-tab t9 --rewe-tab t16 --report /tmp/grocery-cross-shop-audit.md

Manifest schema (canonical goals vs exact observed retailer listings):
{
 "intents": [
   {"id":"fresh_eggs","label":"Fresh eggs","target":30,"unit":"piece","required":true},
   {"id":"tea_ginger","label":"Ginger-lemon tea","target":1,"unit":"pack",
    "group":"tea_total"},
   {"id":"tea_chai","label":"Turmeric chai tea","target":1,"unit":"pack",
    "group":"tea_total"}
 ],
 "groups":[{"id":"tea_total","label":"Tea total","max_quantity":2,"unit":"pack"}],
 "products":[
   {"merchant":"wolt","title":"... 10 Stück","intent_id":"fresh_eggs","units_per_pack":10},
   {"merchant":"rewe","title":"... 10 Stück","intent_id":"fresh_eggs","units_per_pack":10}
 ]
}

Use EXACT verified SKU titles. Different flavors are separate intent IDs unless the
food rules explicitly treat them as interchangeable. Unknown items are blockers:
expand the canonical mapping rather than assuming different text means different food.
"""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import subprocess
import sys
import unicodedata


@dataclass(frozen=True)
class CartLine:
    merchant: str
    title: str
    quantity: int


def normalize_title(value: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def decimal_field(value, label: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f'{label}: invalid quantity {value!r}') from exc
    if not number.is_finite() or number <= 0:
        raise ValueError(f'{label}: quantity must be finite and positive')
    return number


def validate_manifest(manifest: dict) -> None:
    if not isinstance(manifest, dict):
        raise ValueError('Manifest must be a JSON object')
    goals = manifest.get('intents', [])
    if not goals:
        raise ValueError('Manifest needs at least one canonical purchase intent')
    intents = {}
    for goal in goals:
        ident = goal['id']
        if ident in intents:
            raise ValueError('Duplicate intent id: ' + ident)
        decimal_field(goal['target'], ident)
        if not goal.get('unit'):
            raise ValueError(f'{ident}: missing normalized unit')
        intents[ident] = goal
    groups = {}
    for group in manifest.get('groups', []):
        ident = group['id']
        if ident in groups:
            raise ValueError('Duplicate group: ' + ident)
        decimal_field(group['max_quantity'], ident)
        groups[ident] = group
    for goal in goals:
        group_id = goal.get('group')
        if group_id:
            if group_id not in groups:
                raise ValueError(f'{goal["id"]}: missing group {group_id}')
            if groups[group_id]['unit'] != goal['unit']:
                raise ValueError(f'{goal["id"]}: incompatible group units')
    seen_products = set()
    for row in manifest.get('products', []):
        if row['intent_id'] not in intents:
            raise ValueError('Product references missing intent: ' + row['intent_id'])
        if row['merchant'] not in {'wolt', 'rewe', 'flaschenpost'}:
            raise ValueError('Unknown merchant: ' + row['merchant'])
        key = (row['merchant'], normalize_title(row['title']))
        if key in seen_products:
            raise ValueError('Ambiguous retailer SKU mapping: ' + str(key))
        seen_products.add(key)
        decimal_field(row['units_per_pack'], str(key))


def audit(manifest: dict, lines: list[CartLine]) -> dict:
    """Pure deterministic audit. No network or browser mutations."""
    validate_manifest(manifest)
    goals = {x['id']: x for x in manifest['intents']}
    catalogue = {(x['merchant'], normalize_title(x['title'])): x
                 for x in manifest.get('products', [])}
    matched = defaultdict(list)
    unmapped = []
    errors = []
    for line in lines:
        if not isinstance(line.quantity, int) or isinstance(line.quantity, bool) or line.quantity <= 0:
            errors.append(f'Invalid cart count: {line.merchant} / {line.title}: {line.quantity}')
            continue
        key = (line.merchant, normalize_title(line.title))
        row = catalogue.get(key)
        if not row:
            unmapped.append({'merchant':line.merchant, 'title':line.title, 'quantity':line.quantity})
            errors.append(f'UNMAPPED item: {line.merchant} / {line.title} x {line.quantity}')
            continue
        amount = Decimal(line.quantity) * decimal_field(row['units_per_pack'], row['title'])
        matched[row['intent_id']].append({
            'merchant':line.merchant, 'title':line.title,
            'packs':line.quantity, 'amount':amount
        })
    report = []
    aggregates = defaultdict(lambda: Decimal(0))
    for id, goal in goals.items():
        entries = matched.get(id, [])
        actual = sum((item['amount'] for item in entries), Decimal(0))
        target = decimal_field(goal['target'], id)
        vendors = {item['merchant'] for item in entries}
        if actual > target:
            errors.append(f'OVERBUY {goal["label"]}: {actual} {goal["unit"]} across carts vs {target} planned')
        if len(vendors) > 1 and not goal.get('allow_split', False):
            errors.append(f'DUPLICATE SHOP ALLOCATION {goal["label"]}: {", ".join(sorted(vendors))}; choose ONE shop')
        if actual < target and goal.get('required', True):
            errors.append(f'UNSOURCED {goal["label"]}: {actual}/{target} {goal["unit"]}')
        if goal.get('group'):
            aggregates[goal['group']] += actual
        report.append({
            'id':id, 'label':goal['label'], 'unit':goal['unit'],
            'target':str(target), 'actual':str(actual),
            'merchants':sorted(vendors),
            'allocations':[{'merchant':item['merchant'], 'title':item['title'],
                            'packs':item['packs'], 'normalized_quantity':str(item['amount'])}
                           for item in entries]
        })
    group_report = []
    for group in manifest.get('groups', []):
        actual = aggregates[group['id']]
        maximum = decimal_field(group['max_quantity'],group['id'])
        if actual > maximum:
            errors.append(f'GROUP CAP {group["label"]}: {actual}/{maximum} {group["unit"]}')
        group_report.append({'id':group['id'],'label':group['label'],
                             'actual':str(actual),'maximum':str(maximum),'unit':group['unit']})
    return {'ok':not errors, 'errors':errors, 'goals':report,
            'groups':group_report, 'unmapped':unmapped, 'line_count':len(lines)}



def proposed_addition_errors(manifest: dict, lines: list[CartLine],
                             merchant: str, title: str, target_packs: int) -> list[str]:
    """Guard a proposed per-shop SKU target against EVERY shop's cart.

    Missing/not-yet-sourced planned goods are fine mid-build; unknown listings,
    quantity excess and cross-merchant allocation conflicts are NOT.
    """
    if not isinstance(target_packs, int) or isinstance(target_packs,bool) or target_packs <= 0:
        return ['New SKU target must be a positive integer']
    exact=(merchant,normalize_title(title))
    mapping={(p['merchant'],normalize_title(p['title'])):p
             for p in manifest.get('products', [])}
    if exact not in mapping:
        return [f'Unmapped proposed SKU: {merchant} / {title}']
    updated=[]
    matched=0
    for line in lines:
        if (line.merchant,normalize_title(line.title))==exact:
            matched+=1
            updated.append(CartLine(line.merchant,line.title,target_packs))
        else:
            updated.append(line)
    if matched>1:
        return [f'Multiple cart lines match proposed product {merchant} / {title}']
    if matched==0:
        updated.append(CartLine(merchant,title,target_packs))
    result=audit(manifest,updated)
    return [problem for problem in result['errors']
            if not problem.startswith('UNSOURCED ')]

def markdown_report(result: dict) -> str:
    parts = ['# Cross-shop grocery audit',
             '',
             '**Status: ' + ('PASS' if result['ok'] else 'BLOCKED') + '**',
             '',
             '| Food / variant | Target | In all carts | Shops |',
             '| --- | ---: | ---: | --- |']
    for row in result['goals']:
        parts.append(f'| {row["label"]} | {row["target"]} {row["unit"]} | '
                     f'{row["actual"]} {row["unit"]} | {", ".join(row["merchants"]) or "—"} |')
    if result['groups']:
        parts.extend(['','## Category ceilings'])
        for group in result['groups']:
            parts.append(f'- {group["label"]}: {group["actual"]}/{group["maximum"]} {group["unit"]}')
    parts.extend(['','## Problems requiring correction'])
    if result['errors']:
        parts.extend('- ' + error for error in result['errors'])
    else:
        parts.append('None. Every mapped purchase intent respects its overall quota.')
    parts.extend(['','## Verified cart assignments'])
    for goal in result['goals']:
        for alloc in goal['allocations']:
            parts.append(f'- {alloc["merchant"]}: {alloc["title"]} × {alloc["packs"]} '
                         f'= {alloc["normalized_quantity"]} {goal["unit"]} ({goal["label"]})')
    parts.extend(['','**This report does not place an order.**',''])
    return '\n'.join(parts)


def browser_eval(tab: str, script: str) -> list[dict]:
    def cli(*args):
        proc = subprocess.run(['agent-browser', *args], capture_output=True, text=True, timeout=35)
        if proc.returncode:
            raise RuntimeError(f'agent-browser failed: {proc.stderr[:300]}')
        return proc.stdout.strip()
    cli('tab', tab)
    url = cli('get','url')
    if 'wolt.com/' not in url and 'rewe.de/shop/' not in url:
        raise ValueError('Unexpected tab origin: refusing cart read')
    parsed = json.loads(cli('eval', script))
    if not isinstance(parsed, list):
        raise ValueError('Shop cart inaccessible: expected list of actual cart lines')
    return parsed


def read_wolt(tab: str) -> list[CartLine]:
    script = r"""(() => {
      const rows=[...document.querySelectorAll('[data-test-id=CartItem]')];
      if(!rows.length) throw Error('Wolt cart is not open; do not treat missing DOM as empty cart');
      return rows.map(x=>({
        title:x.querySelector('[data-test-id=CartItemName]')?.textContent?.trim(),
        quantity:Number(x.querySelector('[data-test-id=CartItemStepper]')?.value||0)
      }));
    })()"""
    return [CartLine('wolt', r['title'], r['quantity']) for r in browser_eval(tab,script)]


def read_rewe(tab: str) -> list[CartLine]:
    script = r"""(() => {
      const rows=[...document.querySelectorAll('[role=row]')]
        .filter(e=>e.querySelector('[data-testid=lineitem-title]'));
      if(!rows.length) throw Error('REWE cart not visible; do not treat missing DOM as empty cart');
      return rows.map(e=>({
        title:e.querySelector('[data-testid=lineitem-title]')?.textContent?.trim(),
        quantity:Number(e.querySelector('input[aria-label=Bestellmenge]')?.value||0)
      }));
    })()"""
    return [CartLine('rewe', r['title'], r['quantity']) for r in browser_eval(tab,script)]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True, type=Path)
    p.add_argument('--snapshot', type=Path, help='Offline JSON {carts:{wolt:[...],rewe:[...]}} for tests / reruns')
    p.add_argument('--wolt-tab', help='Live Wolt tab with actual cart open')
    p.add_argument('--rewe-tab', help='Live REWE tab with actual basket visible')
    p.add_argument('--report', type=Path, help='Optional output Markdown, e.g. /tmp/...; never Git-track real carts')
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text())
    lines = []
    if args.snapshot:
        obj = json.loads(args.snapshot.read_text())
        for merchant, entries in obj['carts'].items():
            lines.extend(CartLine(merchant,e['title'],e['quantity']) for e in entries)
    else:
        if not args.wolt_tab and not args.rewe_tab:
            p.error('Provide --snapshot or one/more existing browser tabs')
        if args.wolt_tab:
            lines.extend(read_wolt(args.wolt_tab))
        if args.rewe_tab:
            lines.extend(read_rewe(args.rewe_tab))
    result = audit(manifest,lines)
    md = markdown_report(result)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(md,encoding='utf-8')
    print(md)
    return 0 if result['ok'] else 2


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, KeyError, OSError, subprocess.TimeoutExpired) as exc:
        print(f'CART AUDIT FAILED CLOSED: {exc}', file=sys.stderr)
        sys.exit(2)
