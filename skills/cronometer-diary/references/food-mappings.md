# Cronometer Food Mappings

This file stores reusable mappings from the user's real foods to Cronometer database entries. Confirm mappings in Cronometer before using them for automatic diary entry.

Status values:

- `confirmed`: Use this mapping unless the user gives a materially different product.
- `candidate`: Likely mapping, but verify in Cronometer before first use.
- `needs decision`: There is a known tradeoff or ambiguity; ask the user before saving.

## Saved Cronometer Meals

Use these saved meals when the dictated intake matches the bundle. Do not recreate the component ingredients unless the saved meal is missing, changed, or does not match the user's current amounts.

| Meal name | Use when dictated | Included items | Excluded items | Status | Notes |
|---|---|---|---|---|---|
| Standard Breakfast Base | Recurring breakfast base with whey, oats, chia, flaxseed, skim milk, and nut mix at standard amounts | Whey Protein Powder 50 g; Oatmeal, Regular or Quick, Dry 50 g; Chia Seeds 8 g; Flax Seeds, Not Fortified 8 g; Milk, Skim, Fat Free 204.2 g as 200 ml equivalent; Hazelnuts, Raw 10 g; Cashews, Raw 10 g; Almonds, Raw 10 g; Walnuts 10 g; Macadamia Nuts, Raw 10 g | Banana, mandarin, coffee, AG1, creatine, Vitamin D3, extra water | confirmed | Created in Cronometer Foods > Custom Meals. Prefer this over entering the ten component foods individually. |
| Creatine + Water | Standard creatine routine | My Protein, Creatine Monohydrate 10 g; Tap Water 200 ml | Vitamin D3 and other supplements | confirmed | Created in Cronometer Foods > Custom Meals. Use when the user dictates creatine with its usual water. |

## Mapping Table

| User food / product | English search term | Chosen Cronometer entry | Source | Typical measure | Macro comparison | Status | Notes |
|---|---|---|---|---|---|---|---|
| Haferflocken | oats dry OR rolled oats | Oatmeal, Regular or Quick, Dry | NCCDB | g | Confirmed for dry weighed oats. | confirmed | Avoid cooked oatmeal entries when the user weighed dry oats. |
| Whey | whey protein powder | Whey Protein Powder, 18 Grams of Protein per Scoop | NCCDB | g | Generic unknown whey; brand-specific protein content may vary. | confirmed | Use as generic fallback when no brand/macros are provided. If the user gives package macros or brand, compare against possible 24 g or 30 g protein-per-scoop alternatives. |
| Leinsamen | flaxseed OR flax seeds | Flax seeds | NCCDB | g | Confirmed for plain flaxseed. | confirmed | Prefer plain whole or ground flaxseed matching what was eaten. |
| Chia-Samen | chia seeds | Chia Seeds | NCCDB | g | Confirmed for plain chia seeds. | confirmed | Plain chia seeds. |
| Reiswaffeln | rice cake | Rice Cake | NCCDB | g | Confirmed for plain rice cakes. | confirmed | Use generic plain rice cake unless the user specifies a flavored or branded product. |
| Mandarine | mandarin orange OR clementine | Mandarin Orange, Fresh | NCCDB | 1 medium - 2 1/2 inch diameter / 88 g | Confirmed for one medium fresh fruit when no weight is dictated. | confirmed | Use gram weight if the user provides one. |
| Banane | banana | Banana, Fresh | NCCDB | 1 medium - 7 to 7 7/8 inch long / 118 g | Confirmed for one medium fresh fruit when no weight is dictated. | confirmed | Use gram weight if the user provides one. |
| Kiwi | kiwi fruit | Kiwi Fruit, Green | NCCDB | 1 each - 2 inch diameter / 69 g | Confirmed fallback when no explicit medium option appears. | confirmed | Use gram weight if the user provides one. |
| Blaubeeren | blueberries | Blueberries, Fresh | NCCDB | g | Confirmed for fresh blueberries. | confirmed | Use frozen unsweetened only when the user explicitly had frozen berries. |
| Fettarme Milch | low fat milk | Milk, 1 1/2% Fat | NCCDB | cup, 244 g per cup | Confirmed for low-fat/fettarme milk; 300 ml was entered as 1.25 cup. | confirmed | Use 1.25 cup to represent 300 ml unless a better ml measure is available. |
| Filterkaffee | brewed coffee OR coffee prepared from grounds | Coffee, Prepared From Grounds | NCCDB | ml | Confirmed for brewed/filter coffee; typical prep is 20-30 g ground coffee with 500-600 ml water. | confirmed | Use around 550 ml for the usual serving. Do not enter dry coffee grounds. Do not add separate water unless Cronometer clearly does not count coffee as fluid and the user wants separate hydration tracking. |
| Kreatin | creatine monohydrate | My Protein, Creatine Monohydrate | CRDB | g | Confirmed supplement entry; macros are usually irrelevant. | confirmed | Use 5 g when the user dictates the standard dose. |
| Vitamin D3 | vitamin d3 1000 IU | Kirkland, Vitamin D3 1000 IU | CRDB | 1 tablet | Confirmed fallback when no generic 1000 IU entry is available. | confirmed | Use 1 tablet for about 1000 IU unless the user specifies another product or dose. |
| AG1 / Athletic Greens | AG1 | AG1, Daily Foundational Nutrition, 12g Serving | CRDB | g or stick pack - 12 g | Cronometer entry has a 12 g serving; 13 g logs as 43.33 kcal, 2.2 g protein, 6.5 g carbs, 1.1 g fat, with 28 listed nutrients. | confirmed | Prefer this CRDB entry for the user's current AG1 unless they specify a different region, flavor, or label version. |
| Nusskernmischung, current estimate | hazelnuts; cashews; almonds; walnuts; macadamia nuts | Track as separate nuts, not mixed nuts | NCCDB | g | User accepts a rough equal split across five nut types for the recurring mixed box. | confirmed | For a 50 g serving, enter 10 g each: Hazelnuts, Raw; Cashews, Raw; Almonds, Raw; Walnuts; Macadamia Nuts, Raw. |
| Walnuss | walnuts | Walnuts | NCCDB | g | Confirmed as part of estimated mixed nut box. | confirmed | Use for equal-split nut mix unless the user gives a different ratio. |
| Mandel | almonds | Almonds, Raw | NCCDB | g | Confirmed as part of estimated mixed nut box. | confirmed | Use for equal-split nut mix unless the user gives a different ratio. |
| Haselnuss | hazelnuts | Hazelnuts, Raw | NCCDB | g | Confirmed as part of estimated mixed nut box. | confirmed | Use for equal-split nut mix unless the user gives a different ratio. |
| Cashew | cashews | Cashews, Raw | NCCDB | g | Confirmed as part of estimated mixed nut box. | confirmed | Use for equal-split nut mix unless the user gives a different ratio. |
| Macadamia | macadamia nuts | Macadamia Nuts, Raw | NCCDB | g | Confirmed as part of estimated mixed nut box. | confirmed | Use for equal-split nut mix unless the user gives a different ratio. |
| Lachs / fetter Lachs | salmon | TBD | Needs comparison | g | User example: real product may be around 18 g protein and 19 g fat per 100 g; avoid lean salmon entries around 21 g protein and 13 g fat if that mismatches the product. | needs decision | Choose nutrient-rich entry only if fat/protein profile is close enough; otherwise consider branded/CRDB entry. |

## Decision Notes

- Generic whole foods usually map well to `NCCDB` or `USDA`.
- Branded German supermarket entries often have weaker micronutrient coverage, but can be more accurate for processed or fortified products.
- When nutrient coverage and macro accuracy conflict, prefer macro accuracy for materially different foods and ask the user for the tradeoff.
