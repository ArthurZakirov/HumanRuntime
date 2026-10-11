#!/usr/bin/env python3
"""Determine the anchored REWE-vs-Wolt grocery weekend, without drift.

Date supplied means intended WEEKEND (Saturday or Sunday), NOT checkout/delivery
date. For a delayed order (e.g. Monday), pass its original planned weekend;
a delayed delivery does not shift future REWE weekends.
"""
import argparse
from datetime import date, timedelta
from dataclasses import dataclass

ANCHOR_SATURDAY = date(2026, 10, 10)


@dataclass(frozen=True)
class ShoppingCycle:
    weekend_start: date
    next_weekend_start: date
    is_rewe_anchor: bool
    primary_shop: str


def shopping_cycle(nominal_weekend: date) -> ShoppingCycle:
    if nominal_weekend.weekday() not in (5, 6):
        raise ValueError("Supply intended Saturday/Sunday session date, not delivery date.")
    saturday = nominal_weekend - timedelta(days=nominal_weekend.weekday() - 5)
    if saturday < ANCHOR_SATURDAY:
        raise ValueError("Anchor set from October 10, 2026; earlier weekends not covered.")
    weeks = (saturday - ANCHOR_SATURDAY).days // 7
    rewe = weeks % 2 == 0
    return ShoppingCycle(
        weekend_start=saturday,
        next_weekend_start=saturday + timedelta(days=7),
        is_rewe_anchor=rewe,
        primary_shop="REWE" if rewe else "Flink via Wolt"
    )


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weekend", required=True, type=date.fromisoformat, help="Saturday or Sunday YYYY-MM-DD of intended shopping session")
    args=p.parse_args()
    result=shopping_cycle(args.weekend)
    print(f"Intended weekend: {result.weekend_start:%Y-%m-%d}–{(result.weekend_start + timedelta(days=1)):%Y-%m-%d}")
    print(f"Primary shop: {result.primary_shop}")
    print("REWE obligation: " + ("yes – 14-day frozen meat/fish block" if result.is_rewe_anchor else "no – fallback only"))
    print("Weekly fresh fruit & vegetables: due for 7 days regardless of remaining counted stock")
    print(f"Next weekend: {result.next_weekend_start:%Y-%m-%d}")


if __name__ == "__main__":
    main()
