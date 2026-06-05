# KidCoin locale platform

## Concepts

| Layer | Example | Purpose |
|-------|---------|---------|
| **Market** | `vn`, `my`, `ph`, `en` | Business region, currency, default language |
| **Locale** | `vi-VN`, `en-MY`, `ms-MY` | UI strings (JSON bundles) |
| **Speech** | `vi-VN`, `en-US` | TTS / voice recognition (BCP-47) |

## Resolution order

1. URL prefix `/m/{market}/...` (future)
2. Route hints (`/game/english-shooter` → `en`)
3. Cookies `kidcoin_market`, `kidcoin_locale`
4. `Accept-Language`
5. Default `vn` / `vi-VN`

## Add a new country (e.g. Thailand)

1. `registry.py` — `MARKETS["th"]`, `LOCALES["th-TH"]`
2. `messages/th-TH.json` — copy `en.json`, translate
3. Product routes — `/m/th/game/...` or dedicated hub
4. DB content packs — set `locale` on catalog rows

## Templates

```html
{% include "locale/head.html" %}
{{ t('games.math.start_flappy') }}
```

## JavaScript

```html
<script src="/static/js/locale/platform.js"></script>
<script>KidLocale.t('games.math.score', { n: 10 });</script>
```

## API

`GET /api/v1/system/locale` — current market/locale + available list

## Play wallet (sổ cái)

- Bảng cố định: `play_kid_wallets` + `play_wallet_ledger` (không thêm cột khi có game mới).
- Mỗi game học: tài khoản `EARN:{game_id}` trong `accounts_json` (vd `EARN:math_blast`, `EARN:english_math`).
- Thêm chủ đề/game: seed `play_games` + `LEARNING_GAME_IDS` (code) — **không migration**.
