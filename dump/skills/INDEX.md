# Skills Index

Structure: one directory per app type. An app is **shop**, **membership**,
or **community**, or a valid combination (shop+membership, shop+community).
`membership` and `community` are mutually incompatible (backed by different
classic APIs).

Each skill now lives in its own package directory:
`<app_type>/<skill-slug>/SKILL.md`.

Skill frontmatter name format is:
`<app_type>-<skill-slug>`.

Common skills (push-broadcast, traffic-report, weekly-digest) are duplicated
per directory with wording tailored to that context.

`common/` can host cross-app skills that apply to all app types.

## shop/
- [best-sellers](shop/best-sellers/SKILL.md) — rank products: sales, views, conversion
- [catalog-audit](shop/catalog-audit/SKILL.md) — detect incomplete product sheets
- [customer-insights](shop/customer-insights/SKILL.md) — segment customers (VIP, loyal, dormant, one-shot)
- [order-followup](shop/order-followup/SKILL.md) — todo list of orders to process
- [kpi-monitor](shop/kpi-monitor/SKILL.md) — threshold-based daily/weekly KPI health alerts
- [low-performers](shop/low-performers/SKILL.md) — rank worst products by zero/low sales with back-office links
- [orphan-products](shop/orphan-products/SKILL.md) — list products without collections and suggest assignment plan
- [product-launch](shop/product-launch/SKILL.md) — guided creation of a full product
- [promo-campaign](shop/promo-campaign/SKILL.md) — promocode + announcement push
- [promo-performance-review](shop/promo-performance-review/SKILL.md) — pre/during/post promo impact analysis
- [prospect-nurture](shop/prospect-nurture/SKILL.md) — prioritize shop prospects
- [push-broadcast](shop/push-broadcast/SKILL.md) — shop push notification
- [reorder-planner](shop/reorder-planner/SKILL.md) — supplier-ready replenishment queue
- [rfm-segmentation](shop/rfm-segmentation/SKILL.md) — recency/frequency/monetary customer segments
- [stock-check](shop/stock-check/SKILL.md) — stock-out / low-stock audit
- [traffic-report](shop/traffic-report/SKILL.md) — shop analytics
- [weekly-digest](shop/weekly-digest/SKILL.md) — weekly shop business recap

## membership/
- [device-landscape](membership/device-landscape/SKILL.md) — platforms, top devices, top OS-version/platform pairs
- [internal-subscription-grant](membership/internal-subscription-grant/SKILL.md) — create/update/revoke internal subscriptions
- [prospect-followup](membership/prospect-followup/SKILL.md) — prioritize membership prospects
- [push-broadcast](membership/push-broadcast/SKILL.md) — push to all subscribers (no group targeting)
- [subscription-audit](membership/subscription-audit/SKILL.md) — active/expired/churn/at-risk report
- [traffic-report](membership/traffic-report/SKILL.md) — membership app analytics
- [weekly-digest](membership/weekly-digest/SKILL.md) — weekly membership business recap

## community/
- [device-landscape](community/device-landscape/SKILL.md) — platforms, top devices, top OS-version/platform pairs
- [push-broadcast](community/push-broadcast/SKILL.md) — push to all or to a community group
- [traffic-report](community/traffic-report/SKILL.md) — community app analytics
- [weekly-digest](community/weekly-digest/SKILL.md) — weekly community recap

## Cross-cutting design principles

Every skill in this directory follows these five rules. If you're adding
or modifying a skill, keep them in mind.

**A. Pagination & volumes** — On large datasets (customers, orders,
products, prospects, subscriptions), filter server-side (`updated_at`,
`status`, date windows) instead of full-paginating. Only go deep when
the user explicitly asks for it.

**B. Fuzzy matching vs strict ID** — If the user gives a name (product,
collection, tag, group, prospect), do a list lookup and fuzzy-match. If
ambiguous, ask them to pick from a numbered list. Never guess.

**C. Next possible actions** — Every skill ends with a "Next possible
actions" block suggesting 2–3 related skills to run next. Fluidify the
workflow — don't leave the user at a dead end.

**D. Timezones & relative dates** — If the user uses relative dates
("tomorrow", "next week", "end of month") on any temporal field, confirm
the intended timezone. Default to UTC if unknown, but ask first.

**E. `meta_get_tool_plan` discipline** — Only call it when a mutation
fails with a missing or wrongly-typed parameter. Do not call it
preventively — it burns context.

## Tool scope reminders

| Tool family | Shop | Membership | Community |
|---|---|---|---|
| `shop_*` | ✓ | — | — |
| `classic_*_subscription*`, `classic_*_prospect*` | — | ✓ | — |
| `classic_create_push_broadcast` | — | ✓ | ✓ |
| Push to group (`ForGroup`) | — | — | ✓ |
| Analytics (`*_list_page_views`, launches, sessions, devices…) | ✓ | ✓ | ✓ |
| `classic_list_mobile_os_distribution`, `classic_list_os_versions_global`, `classic_list_devices_global` | — | ✓ | ✓ |
