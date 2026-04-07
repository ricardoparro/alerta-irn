# Alerta IRN

Monitors [IRN](https://siga.marcacaodeatendimento.pt/Senhas/TemposEspera) queue availability for **Passaporte - Pedido** and sends Telegram notifications when tickets ("senhas") become available.

Currently configured for **Oeiras and Cascais** locations, but can be easily modified by editing the `LOCAIS_FILTER` and form data parameters in `checker.py`.

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get the token
2. Send `/start` to your bot, then get your chat ID from `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Configure:
   ```bash
   cp .env.example .env
   # fill in TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
   ```
4. Run:
   ```bash
   docker compose up -d
   ```

## Configuration

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token from BotFather | required |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | required |
| `CHECK_INTERVAL` | Seconds between checks | `1200` (20 min) |

## Customization

To monitor different locations or services, edit `checker.py`:

- `LOCAIS_FILTER` — list of location name substrings to match (e.g. `["cascais", "oeiras"]`)
- `IdDistrito` — district ID (`11` = Lisboa)
- `IdEntidade` — entity ID (`176` = IRN Registo)
- `IdSenha` — service ID (`912` = Passaporte - Pedido)
