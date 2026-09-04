#!/usr/bin/env python3
"""A CLI é chamada por caminho absoluto do plugin, nunca relativo.

Instalado, o plugin roda com o diretório de trabalho no projeto do cliente —
onde `bin/dk` não existe. Skill que chama `bin/dk` funciona no desenvolvimento
do próprio plugin e quebra em todo uso real. `${CLAUDE_PLUGIN_ROOT}` é o que o
Claude Code define apontando para a raiz do plugin instalado."""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
errors = []

RELATIVO = re.compile(r'(?<![/{])\bbin/dk\b')

for arquivo in sorted(list(RAIZ.glob('skills/*/SKILL.md'))
                      + list(RAIZ.glob('agents/*.md'))):
    texto = arquivo.read_text(encoding='utf-8')
    for linha in texto.splitlines():
        if RELATIVO.search(linha) and 'CLAUDE_PLUGIN_ROOT' not in linha:
            errors.append(f'{arquivo.relative_to(RAIZ)}: chamada relativa — '
                          f'{linha.strip()[:70]}')

cli = RAIZ / 'bin' / 'dk'
if not os.access(cli, os.X_OK):
    errors.append('bin/dk não é executável — instalado, ninguém o roda')

# A CLI resolve a própria raiz: rodar de outro diretório não pode quebrá-la.
r = subprocess.run([sys.executable, str(cli), '--help'], cwd='/',
                   capture_output=True, text=True)
if r.returncode != 0:
    errors.append(f'a CLI não roda fora da raiz do plugin: {r.stderr[:200]}')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
