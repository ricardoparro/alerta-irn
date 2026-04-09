import logging
import os
import time

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_URL = "https://siga.marcacaodeatendimento.pt"
LOCAIS_FILTER = ["cascais", "oeiras"]

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "1200"))


def get_session() -> requests.Session:
    s = requests.Session()
    r = s.get(f"{BASE_URL}/Senhas/TemposEspera", timeout=30)
    r.raise_for_status()
    return s


def check_senhas(session: requests.Session) -> list[dict]:
    r = session.post(
        f"{BASE_URL}/Senhas/GetLocais",
        data={
            "IdDistrito": "11",
            "IdEntidade": "176",
            "IdSenha": "912",
            "IdInstituicaoSelecionada": "3",
            "Latitude": "0",
            "Longitude": "0",
            "EstadoLocalizacao": "0",
        },
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    r.raise_for_status()
    locais = r.json()

    noteworthy = []
    for item in locais:
        name = item["nome"].lower()
        if not any(f in name for f in LOCAIS_FILTER):
            continue
        servico = item["servico"]
        if servico["estado"].upper() not in ("SENHA INIBIDA", "FECHADO"):
            noteworthy.append(item)
    return noteworthy


def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    r = requests.post(
        url,
        json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
        timeout=15,
    )
    r.raise_for_status()
    log.info("Telegram notification sent")


def format_message(available: list[dict]) -> str:
    lines = ["🚨 <b>Alerta IRN - Passaporte!</b>\n"]
    for item in available:
        s = item["servico"]
        lines.append(
            f"📍 <b>{item['nome']}</b>\n"
            f"   Estado: {s['estado']}\n"
            f"   Pessoas em espera: {s['utentesEmEspera']}\n"
            f"   Horário: {s['horario']}"
        )
    lines.append(
        f"\n🔗 <a href='{BASE_URL}/Senhas/TemposEspera'>Tirar senha no site</a>"
    )
    return "\n".join(lines)


def main() -> None:
    log.info(
        "Alerta IRN started — checking every %d seconds for: %s",
        CHECK_INTERVAL,
        ", ".join(LOCAIS_FILTER),
    )

    while True:
        try:
            session = get_session()
            available = check_senhas(session)
            if available:
                names = [a["nome"] for a in available]
                log.info("SENHAS DISPONÍVEIS: %s", ", ".join(names))
                send_telegram(format_message(available))
            else:
                log.info("Nenhuma senha disponível")
        except Exception:
            log.exception("Error during check")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
