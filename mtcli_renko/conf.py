import os

from mtcli.conf import config

CHAVE = os.getenv("CHAVE", config["DEFAULT"].get("chave", fallback="funcionando"))
