#!/usr/bin/env python3
"""Cada arquivo recebe tipo, linguagem, categoria e custo estimado."""
from __future__ import annotations
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import classify  # noqa: E402

errors = []

casos = [
    ({'caminho': 'src/app.py', 'bytes': 400, 'ext': '.py'},
     {'tipo': 'source', 'linguagem': 'python'}),
    ({'caminho': 'package.json', 'bytes': 800, 'ext': '.json'},
     {'tipo': 'config', 'categoria': 'manifesto'}),
    ({'caminho': 'README.md', 'bytes': 1200, 'ext': '.md'},
     {'tipo': 'doc', 'categoria': 'documentacao-raiz'}),
    ({'caminho': 'tests/test_app.py', 'bytes': 300, 'ext': '.py'},
     {'tipo': 'test'}),
    ({'caminho': 'logo.png', 'bytes': 50000, 'ext': '.png'},
     {'tipo': 'asset', 'binario': True}),
]

for entrada, esperado in casos:
    r = classify.classificar(dict(entrada))
    for chave, valor in esperado.items():
        if r.get(chave) != valor:
            errors.append(
                f"{entrada['caminho']}: {chave} esperado {valor!r}, veio {r.get(chave)!r}")

py = classify.classificar({'caminho': 'src/app.py', 'bytes': 400, 'ext': '.py'})
if py['tokens_estimados'] != 100:
    errors.append(f"tokens de 400 B deveriam ser 100, vieram {py['tokens_estimados']}")

png = classify.classificar({'caminho': 'logo.png', 'bytes': 50000, 'ext': '.png'})
if png['tokens_estimados'] != 0:
    errors.append('binário não custa token de leitura; deveria ser 0')

if not classify.REGRA_TOKENS:
    errors.append('a regra de conversão precisa ser declarada, não implícita')

for e in errors:
    print(e)
sys.exit(1 if errors else 0)
