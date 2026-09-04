#!/usr/bin/env python3
"""A versão do pacote vive em `.claude-plugin/plugin.json` e em nenhum outro lugar.

Qualquer outro arquivo que precise da versão a recebe daqui, gerada. O Kit anterior
declarava a versão em quatro arquivos e dois já divergiam (achado DK-002)."""
from __future__ import annotations
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PLUGIN = RAIZ / '.claude-plugin' / 'plugin.json'


def versao_canonica() -> str:
    return json.loads(PLUGIN.read_text(encoding='utf-8'))['version']


def fontes() -> dict:
    """Todo arquivo que declara versão, mapeado para o valor que ele declara.

    Um arquivo novo que passe a declarar versão entra aqui, ou o teste não o vê."""
    encontradas = {'.claude-plugin/plugin.json': versao_canonica()}
    marketplace = RAIZ / '.claude-plugin' / 'marketplace.json'
    if marketplace.exists():
        dados = json.loads(marketplace.read_text(encoding='utf-8'))
        for plugin in dados.get('plugins', []):
            encontradas['.claude-plugin/marketplace.json'] = plugin.get('version', '')
    return encontradas
