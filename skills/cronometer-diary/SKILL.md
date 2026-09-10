---
name: cronometer-diary
description: Log dictated meals in Cronometer Diary and maintain reusable mappings from real foods to nutrient-rich Cronometer database entries.
---

# Cronometer Diary

Use this skill when the user asks to track food in Cronometer, add diary entries from dictation, or improve the mapping between real products and Cronometer foods.

## Goal

The user's preferred workflow is voice-first: they weigh food in the kitchen, dictate items such as "Breakfast, 50 grams oats, 10 grams flaxseed", and expect Cronometer Diary to be filled without manually using the app. Keep the spoken interaction short. Ask follow-up questions only when needed to avoid materially wrong entries.

## Source Selection

Prefer Cronometer entries with broad micronutrient coverage while staying close to the food actually eaten.

Source priority:

1. `NCCDB` when a generic entry is a close match.
2. `USDA` when no suitable `NCCDB` match exists.
3. `CRDB` or branded/barcode entries when the product is processed, fortified, recipe-specific, or the generic macro profile is too far from the real product.

Do not choose a richer entry if its macros are materially unlike the consumed product. For example, do not map a fatty salmon product to a lean salmon entry just because the lean entry has more micronutrients. If the tradeoff is unclear, explain the options and ask the user which to use before saving.

Search in Cronometer using English food terms. German product names should be translated or mapped to stable English search terms before searching.

## Mapping Reference

Before searching from scratch, read [references/food-mappings.md](references/food-mappings.md). Use confirmed mappings exactly unless the user's dictated product clearly differs from the mapped product.

Prefer saved Cronometer Custom Meals over re-entering their individual ingredients when the dictated food matches a confirmed meal bundle. The user has approved these reusable meals:

- `Standard Breakfast Base`: whey, dry oats, chia seeds, flaxseed, skim milk, and the five-part nut mix. Use this meal instead of adding those ingredients one by one when the user dictates the recurring breakfast base or the same ingredient set.
- `Creatine + Water`: creatine monohydrate plus water. Use this meal when the user dictates the paired creatine routine.

Do not use a saved meal if the user changes one of its component amounts, omits a component, or adds optional foods that should stay separate. Banana, mandarin, coffee, AG1, Vitamin D3, and extra water are not part of `Standard Breakfast Base` unless the user later changes the meal definition.

When a new mapping is identified, update the mapping reference with:

- German/user-facing product name.
- English Cronometer search term.
- Chosen Cronometer food name.
- Source, such as `NCCDB`, `USDA`, or `CRDB`.
- Typical unit or measure.
- Macro comparison against the real product when known.
- Status: `confirmed`, `candidate`, or `needs decision`.
- Notes explaining tradeoffs or why a branded entry is required.

## Diary Entry Workflow

In Cronometer Diary:

1. Open `Diary`.
2. If the dictated item matches a confirmed saved meal, add the saved meal instead of its component foods.
3. Otherwise select `FOOD`.
4. Search for the mapped English food term or the confirmed Cronometer food name.
5. Select the intended result, checking source and name.
6. Set `Diary Group`, usually `Breakfast`, `Lunch`, `Dinner`, or `Snacks`.
7. Set amount and measure from the user's dictation.
8. Click `ADD TO DIARY` only after the item, source, amount, measure, date, and diary group are clear.

Never save an entry from exploration alone. Saving is appropriate only when the user has provided the actual food, amount, unit, and intended meal/date, or has explicitly approved the final entry.

## Dictation Parsing

For each dictated item, extract:

- Date, defaulting to today only if the user is describing the current meal.
- Diary group or meal.
- Food name.
- Amount.
- Unit or serving description.
- Brand or product variant when relevant.

If the user dictates several items in one stream, batch them mentally and enter them one by one. Confirm only the ambiguous items; do not repeat obvious entries back at length.

## When To Ask

Ask before saving when:

- Multiple plausible Cronometer entries have different macro profiles.
- The item is processed, fortified, or brand-specific.
- The dictated unit cannot be mapped to a Cronometer measure.
- The mapped entry is marked `needs decision`.
- The amount or meal is missing.
